"""
File name      : backend.py
Description    : The central backend engine for the Smart Attendance System.
                 Manages the database, liveness detection, and all recognition logic.
Author         : Chaitanya
"""

import sqlite3
import json
import math
import cv2
import face_recognition
import mediapipe as mp
import numpy as np

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

        # Initialize MediaPipe Face Mesh for liveness detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

        # Liveness detection constants
        self.LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.EAR_THRESHOLD = 0.25
        self.BLINK_FRAMES_MIN = 2
        self.BLINK_FRAMES_MAX = 5

    # ==============================================================================
    # SECTION 1: DATABASE MANAGEMENT
    # ==============================================================================
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
        iris_code_json = json.dumps(iris_code) # Also store iris code as JSON
        
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

    # ==============================================================================
    # SECTION 2: LIVENESS & RECOGNITION LOGIC
    # ==============================================================================
    
    def check_liveness(self, frame, blink_counter):
        """
        Function name  : check_liveness
        Description    : Checks for a blink in the given frame to verify liveness
                         using the Eye Aspect Ratio (EAR) algorithm.
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

    def recognize_face(self, frame, known_embeddings, known_names):
        """
        Performs face recognition on a given frame.
        """
        try:
            live_face_locations = face_recognition.face_locations(frame)
            live_face_embeddings = face_recognition.face_encodings(frame, live_face_locations)

            for face_embedding in live_face_embeddings:
                matches = face_recognition.compare_faces(known_embeddings, face_embedding, tolerance=0.6)
                face_distances = face_recognition.face_distance(known_embeddings, face_embedding)
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        return known_names[best_match_index] # Return the name of the matched person
        except Exception as e:
            print(f"Backend Error: An error occurred during face recognition: {e}")
        
        return None # Return None if no match is found

    # --- Helper methods for liveness ---
    def _calculate_ear(self, landmarks, eye_indices):
        v1 = self._euclidean_distance(landmarks[eye_indices[1]], landmarks[eye_indices[5]])
        v2 = self._euclidean_distance(landmarks[eye_indices[2]], landmarks[eye_indices[4]])
        h = self._euclidean_distance(landmarks[eye_indices[0]], landmarks[eye_indices[3]])
        if h == 0: return 0.0
        return (v1 + v2) / (2.0 * h)

    @staticmethod
    def _euclidean_distance(point1, point2):
        return math.dist(point1, point2)