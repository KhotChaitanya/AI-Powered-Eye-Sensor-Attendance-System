"""
File name      : backend.py
Description    : The central backend engine for the Smart Attendance System.
                 Manages the database, liveness detection, and all recognition logic.
Author         : Chaitanya
"""

# ==============================================================================
# SECTION 1: IMPORTS
# ==============================================================================
import sqlite3
import json
import math
import cv2
import face_recognition
import mediapipe as mp
import numpy as np
import time

# ==============================================================================
# SECTION 2: THE MAIN BACKEND CLASS
# ==============================================================================
class AttendanceSystem:
    """
    Manages all backend logic for the attendance system.
    """
    def __init__(self, db_path='users.db'):
        """
        Initializes the system, sets up the database, and loads MediaPipe models.
        """
        self.db_path = db_path
        self._setup_database()

        # --- Liveness Detection Setup ---
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
        self.LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.EAR_THRESHOLD = 0.25
        self.BLINK_FRAMES_MIN = 2
        self.BLINK_FRAMES_MAX = 5

        # --- State Management for the Workflow ---
        self.workflow_state = "WAITING_FOR_FACE"
        self.blink_counter = 0
        self.last_state_change_time = time.time()
        self.verified_name = None

    # --------------------------------------------------------------------------
    # Subsection 2.1: Database Management (Author: Chaitanya)
    # --------------------------------------------------------------------------
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

    def add_user(self, name, embedding, iris_code):
        """
        Adds a new user profile (name, face embedding, and iris code) to the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        embedding_json = json.dumps(embedding)
        iris_code_json = json.dumps(iris_code)
        
        cursor.execute("INSERT INTO users (name, embedding, iris_code) VALUES (?, ?, ?)",
                       (name, embedding_json, iris_code_json))
        conn.commit()
        conn.close()
        print(f"Backend: User '{name}' has been added to the database.")

    def load_known_users(self):
        """
        Loads all user profiles from the database into memory.
        """
        known_embeddings = []
        known_iris_codes = []
        known_names = []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, embedding, iris_code FROM users")
        rows = cursor.fetchall()

        for row in rows:
            known_names.append(row[0])
            known_embeddings.append(np.array(json.loads(row[1])))
            known_iris_codes.append(np.array(json.loads(row[2])))
            
        conn.close()
        print("Backend: Loaded known user profiles from the database.")
        return known_names, known_embeddings, known_iris_codes

    # --------------------------------------------------------------------------
    # Subsection 2.2: Main Workflow Orchestrator (Author: Chaitanya)
    # --------------------------------------------------------------------------
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
                self.workflow_state = "CHECKING_LIVENESS"
                self.last_state_change_time = time.time()

        # --- State 2: A face is present, check for a blink ---
        elif self.workflow_state == "CHECKING_LIVENESS":
            status_message = "Please Blink to Verify"
            status_color = (0, 0, 255)
            
            is_live, self.blink_counter = self._check_liveness_internal(frame, self.blink_counter)
            if is_live:
                self.workflow_state = "PERFORMING_IRIS_SCAN"
                self.last_state_change_time = time.time()

        # --- State 3: Liveness confirmed, perform iris scan ---
        elif self.workflow_state == "PERFORMING_IRIS_SCAN":
            status_message = "Liveness Verified! Move Closer for Iris Scan"
            status_color = (0, 255, 0)
            
            matched_name = self._recognize_iris_placeholder()
            if matched_name:
                self.verified_name = matched_name
                self.workflow_state = "VERIFIED"
                self.last_state_change_time = time.time()

        # --- State 4: User verified, show success message then reset ---
        elif self.workflow_state == "VERIFIED":
            status_message = f"Attendance Marked for {self.verified_name}"
            status_color = (0, 255, 0)
            if time.time() - self.last_state_change_time > 3:
                self.workflow_state = "WAITING_FOR_FACE"
                self.verified_name = None

        return status_message, status_color

    # --------------------------------------------------------------------------
    # Subsection 2.3: Core AI Logic
    # --------------------------------------------------------------------------
    def _recognize_iris_placeholder(self):
        """
        !!! PLACEHOLDER for Iris Recognition Engine !!!
        Author         : Himanshu (to be implemented)
        """
        if time.time() - self.last_state_change_time > 2:
            return "Chaitanya (Simulated)" 
        return None

    def _check_liveness_internal(self, frame, blink_counter):
        """
        Function name  : _check_liveness_internal
        Description    : Internal helper method for blink detection using EAR.
        Author         : Himanshu
        """
        is_live = False
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = frame.shape
                landmarks = [(lm.x * w, lm.y * h) for lm in face_landmarks.landmark]
                left_ear = self._calculate_ear(landmarks, self.LEFT_EYE_INDICES)
                right_ear = self._calculate_ear(landmarks, self.RIGHT_EYE_INDICES)
                ear = (left_ear + right_ear) / 2.0

                if ear < self.EAR_THRESHOLD:
                    blink_counter += 1
                else:
                    if self.BLINK_FRAMES_MIN <= blink_counter <= self.BLINK_FRAMES_MAX:
                        is_live = True
                    blink_counter = 0
        else:
            blink_counter = 0
        return is_live, blink_counter

    def _calculate_ear(self, landmarks, eye_indices):
        v1 = self._euclidean_distance(landmarks[eye_indices[1]], landmarks[eye_indices[5]])
        v2 = self._euclidean_distance(landmarks[eye_indices[2]], landmarks[eye_indices[4]])
        h = self._euclidean_distance(landmarks[eye_indices[0]], landmarks[eye_indices[3]])
        if h == 0: return 0.0
        return (v1 + v2) / (2.0 * h)

    @staticmethod
    def _euclidean_distance(point1, point2):
        return math.dist(point1, point2)
