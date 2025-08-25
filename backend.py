"""
File name      : backend.py
Description    : The central backend engine for the Smart Attendance System.
Author         : Chaitanya
Contributor    : Himanshu (Core Engine)
"""
import sqlite3
import json
import cv2
import face_recognition
import numpy as np
import time
import iris_engine # Import Friend 1's new engine

class AttendanceSystem:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self._setup_database()
        # --- NEW: Load known users into memory on startup ---
        self.known_names, self.known_embeddings, self.known_iris_codes = self.load_known_users()
        
        # --- State Management for the Workflow ---
        self.workflow_state = "WAITING_FOR_FACE"
        self.blink_counter = 0
        self.last_state_change_time = time.time()
        self.verified_name = None

    def _setup_database(self):
        """
        Creates the database and the 'users' table with the new schema.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                embedding TEXT NOT NULL,
                iris_code TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("Backend: Database is set up and ready.")

    def add_user(self, name, frame):
        """
        MODIFIED: Now takes a full frame to generate both embedding and iris code.
        """
        try:
            # --- Face Embedding Logic ---
            face_locations = face_recognition.face_locations(frame)
            if not face_locations:
                return False, "No face detected."
            embedding = face_recognition.face_encodings(frame, face_locations)[0].tolist()

            # --- Iris Code Logic (from Friend 1) ---
            iris_template = iris_engine.create_iris_code(frame)
            # Convert boolean arrays to lists of 0s and 1s for JSON storage
            iris_code_list = [int(b) for b in iris_template.code]
            iris_mask_list = [int(b) for b in iris_template.mask]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            embedding_json = json.dumps(embedding)
            # Store both code and mask
            iris_json = json.dumps({'code': iris_code_list, 'mask': iris_mask_list})
            
            cursor.execute("INSERT INTO users (name, embedding, iris_code) VALUES (?, ?, ?)",
                           (name, embedding_json, iris_json))
            conn.commit()
            conn.close()
            # Reload known users after adding a new one
            self.known_names, self.known_embeddings, self.known_iris_codes = self.load_known_users()
            return True, f"User '{name}' enrolled successfully."
        except Exception as e:
            return False, f"Enrollment failed: {e}"

    def load_known_users(self):
        """
        Loads all user profiles from the database into memory.
        """
        known_names, known_embeddings, known_iris_codes = [], [], []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, embedding, iris_code FROM users")
            rows = cursor.fetchall()
            for row in rows:
                known_names.append(row[0])
                known_embeddings.append(np.array(json.loads(row[1])))
                # Recreate the IrisTemplate object from stored data
                iris_data = json.loads(row[2])
                code = np.array(iris_data['code'], dtype=bool)
                mask = np.array(iris_data['mask'], dtype=bool)
                known_iris_codes.append(iris_engine.IrisTemplate(code=code, mask=mask))
            conn.close()
        except Exception as e:
            print(f"Database Error: Could not load users. DB might be empty. Error: {e}")
        return known_names, known_embeddings, known_iris_codes

    def run_attendance_check(self, frame):
        """
        This is the main "brain" function the GUI will call in a loop.
        """
        status_message = "Initializing..."
        status_color = (200, 200, 0)

        # --- State 1: Waiting for a face to appear ---
        if self.workflow_state == "WAITING_FOR_FACE":
            status_message = "Please Look at the Camera"
            face_locations = face_recognition.face_locations(frame, model="hog")
            if len(face_locations) > 0:
                self.workflow_state = "PERFORMING_IRIS_SCAN" # Skipping liveness for now
                self.last_state_change_time = time.time()

        # --- State 2: Liveness confirmed, perform iris scan ---
        elif self.workflow_state == "PERFORMING_IRIS_SCAN":
            status_message = "Scanning Iris..."
            status_color = (0, 255, 0)
            
            matched_name = self._recognize_iris(frame)
            if matched_name:
                self.verified_name = matched_name
                self.workflow_state = "VERIFIED"
                self.last_state_change_time = time.time()

        # --- State 3: User verified, show success message then reset ---
        elif self.workflow_state == "VERIFIED":
            status_message = f"Attendance Marked for {self.verified_name}"
            status_color = (0, 255, 0)
            if time.time() - self.last_state_change_time > 3:
                self.workflow_state = "WAITING_FOR_FACE"
                self.verified_name = None

        return status_message, status_color

    def _recognize_iris(self, frame):
        """
        Author: Himanshu (Engine), Chaitanya (Integration)
        """
        try:
            live_template = iris_engine.create_iris_code(frame)
            
            if not self.known_iris_codes:
                return None # No users enrolled

            best_distance = 1.0
            best_match_name = None

            for i, known_template in enumerate(self.known_iris_codes):
                distance, _ = iris_engine.compare_iris_codes(live_template, known_template)
                if distance < best_distance:
                    best_distance = distance
                    best_match_name = self.known_names[i]
            
            if iris_engine.is_match(best_distance):
                return best_match_name
        except Exception as e:
            # This can happen if no eye is found in the frame
            # print(f"Iris recognition error: {e}")
            pass
        return None
