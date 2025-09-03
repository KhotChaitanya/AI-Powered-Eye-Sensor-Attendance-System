"""
File name      : backend.py
Description    : The central backend engine for the Smart Attendance System.
Author         : Chaitanya
Contributor    : Himanshu (Liveness Engine)
"""
import sqlite3
import json
import cv2
import face_recognition
import numpy as np
import time
import os
import csv
from datetime import datetime
from scipy.spatial import distance as dist
import uuid

class AttendanceSystem:
    def __init__(self, db_path='users.db'):
        """
        Function name  : __init__
        Description    : Initializes the system, sets up the database.
        Author         : Chaitanya
        """
        self.db_path = db_path
        self._setup_database()
        self.known_users = self.load_known_users()
        self.reset_workflow()

        # --- Constants ---
        self.EAR_THRESHOLD = 0.21
        self.BLINK_FRAMES_MIN = 2
        self.BLINK_FRAMES_MAX = 6
        self.VERIFICATION_DURATION = 5

    def reset_workflow(self):
        """
        Function name  : reset_workflow
        Description    : Resets the state of the attendance check workflow.
        Author         : Chaitanya
        """
        self.workflow_state = "WAITING_FOR_FACE"
        self.blink_counter = 0
        self.last_state_change_time = time.time()
        self.pending_verification_user = None
        self.scan_progress = 0
        print("Backend: Workflow has been reset.")

    def _setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                embedding TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("Backend: Database is set up and ready.")

    def add_user(self, name, frame):
        """
        Automatically generates a unique ID (UUID) for the new user.
        """
        try:
            face_locations = face_recognition.face_locations(frame)
            if not face_locations:
                return False, "No face detected. Please ensure your face is well-lit and centered."
            if len(face_locations) > 1:
                return False, "Multiple faces detected. Please ensure only one person is in the frame."
            
            embedding = face_recognition.face_encodings(frame, face_locations)[0].tolist()
            user_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            embedding_json = json.dumps(embedding)
            cursor.execute("INSERT INTO users (user_id, name, embedding) VALUES (?, ?, ?)", 
                           (user_id, name, embedding_json))
            conn.commit()
            conn.close()
            
            self.known_users = self.load_known_users()
            return True, f"User '{name}' enrolled successfully with ID: {user_id}"
        except Exception as e:
            return False, f"Enrollment failed: {e}"

    def load_known_users(self):
        users = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, name, embedding FROM users")
            rows = cursor.fetchall()
            for row in rows:
                users.append({
                    "user_id": row[0],
                    "name": row[1],
                    "embedding": np.array(json.loads(row[2]))
                })
            conn.close()
        except Exception as e:
            print(f"Database Error: {e}")
        return users

    def has_enrolled_users(self):
        """
        Function name  : has_enrolled_users
        Description    : Checks if there are any enrolled users in the system.
        Author         : Chaitanya
        """
        return len(self.known_users) > 0

    def log_attendance(self, user):
        """
        Function name  : log_attendance
        Description    : Creates a formatted CSV with headers for logging attendance.
                         Now includes User ID column for better tracking.
        Author         : Chaitanya
        """
        file_exists = os.path.isfile('attendance.csv')
        with open('attendance.csv', 'a', newline='') as f:
            headers = ['Sr No', 'User ID', 'Username', 'Status', 'Timestamp']
            csv_writer = csv.writer(f)
            
            # Determine the next serial number
            sr_no = 1
            if file_exists and os.path.getsize('attendance.csv') > 0:
                # Read existing file to count rows
                with open('attendance.csv', 'r') as read_file:
                    reader = csv.reader(read_file)
                    rows = list(reader)
                    if len(rows) > 0 and rows[0] == headers:
                        # Header exists, count data rows
                        sr_no = len(rows)
                    else:
                        # No header or different format, add header
                        csv_writer.writerow(headers)
            else:
                # File doesn't exist or is empty, add header
                csv_writer.writerow(headers)
            
            # Write attendance record
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([sr_no, user['user_id'], user['name'], 'Present', timestamp])
        
        print(f"Attendance logged for {user['name']} (ID: {user['user_id']}) at {timestamp}")

    def _compute_ear(self, eye):
        """
        Function name  : _compute_ear
        Description    : Computes EAR Ratio
        Author         : Himanshu
        """
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        if C == 0: return 0.0
        return (A + B) / (2.0 * C)

    def _check_liveness_internal(self, face_landmarks_list):
        """
        Function name  : _check_liveness_internal
        Description    : Core liveness detection engine.
        Author         : Himanshu
        """
        if not face_landmarks_list: return False
        landmarks = face_landmarks_list[0]
        if "left_eye" not in landmarks or "right_eye" not in landmarks: return False
        ear = (self._compute_ear(landmarks["left_eye"]) + self._compute_ear(landmarks["right_eye"])) / 2.0
        if ear < self.EAR_THRESHOLD: self.blink_counter += 1
        else:
            if self.BLINK_FRAMES_MIN <= self.blink_counter <= self.BLINK_FRAMES_MAX:
                self.blink_counter = 0
                return True
            self.blink_counter = 0
        return False

    def run_attendance_check(self, frame, face_landmarks_list):
        """
        Function name  : run_attendance_check
        Description    : The main state machine for the verification workflow.
        Author         : Chaitanya
        """
        status_message = "Initializing..."
        status_color = (200, 200, 0) # Neutral yellow
        self.scan_progress = 0
        
        # Check if there are any enrolled users
        if not self.has_enrolled_users():
            status_message = "No users enrolled. Please enroll users first."
            status_color = (0, 0, 255) # Red for error
            return status_message, status_color, self.scan_progress
        
        if self.workflow_state == "WAITING_FOR_FACE":
            status_message = "Please Look at the Camera"
            if face_landmarks_list and self.known_users:
                known_embeddings = [user["embedding"] for user in self.known_users]
                face_locations = face_recognition.face_locations(frame)
                if not face_locations: return status_message, status_color, self.scan_progress
                
                live_embedding = face_recognition.face_encodings(frame, face_locations)[0]
                face_distances = face_recognition.face_distance(known_embeddings, live_embedding)
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if face_distances[best_match_index] < 0.6:
                        self.pending_verification_user = self.known_users[best_match_index]
                        self.workflow_state = "CHECKING_LIVENESS"
                        self.blink_counter = 0
                        self.last_state_change_time = time.time()
                    else:
                        status_message = "User not recognized. Please enroll first."
                        status_color = (0, 0, 255) # Red for error
                else:
                    status_message = "No matching user found. Please enroll first."
                    status_color = (0, 0, 255) # Red for error

        elif self.workflow_state == "CHECKING_LIVENESS":
            status_message = f"Welcome {self.pending_verification_user['name']}! Please Blink."
            status_color = (0, 165, 255) # Informative orange
            if self._check_liveness_internal(face_landmarks_list):
                self.log_attendance(self.pending_verification_user)
                self.workflow_state = "VERIFYING"
                self.last_state_change_time = time.time()
            elif time.time() - self.last_state_change_time > 10: # Timeout
                self.reset_workflow()

        elif self.workflow_state == "VERIFYING":
            status_message = "Verifying..."
            status_color = (0, 255, 0) # Green for success
            elapsed_time = time.time() - self.last_state_change_time
            self.scan_progress = min((elapsed_time / self.VERIFICATION_DURATION) * 100, 100)
            if elapsed_time > self.VERIFICATION_DURATION:
                self.workflow_state = "FINAL_SUCCESS"

        elif self.workflow_state == "FINAL_SUCCESS":
            status_message = f"Attendance Marked for {self.pending_verification_user['name']}"
            status_color = (0, 255, 0)
            self.scan_progress = 100

        return status_message, status_color, self.scan_progress
