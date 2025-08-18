"""
File name      : app.py
Description    : Main application for the Smart Attendance System.
                 Integrates the UI, database, and core AI logic.
Author         : Chaitanya
"""

# ==============================================================================
# SECTION 1: IMPORTS
# ==============================================================================
import cv2
import face_recognition
import sqlite3
import json
import numpy as np
import vision_utils as vutils # Helper module for liveness logic

# ==============================================================================
# SECTION 2: DATABASE MODULE
# ==============================================================================
def load_known_faces():
    """
    Function name  : load_known_faces
    Description    : Connects to the SQLite database and loads all registered
                     user profiles (names and embeddings) into memory.
    Author         : Chaitanya
    """
    # Task: Connect to the database and fetch all known user profiles.
    known_face_embeddings = []
    known_face_names = []
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, embedding FROM users")
    rows = cursor.fetchall()
    
    for row in rows:
        name = row[0]
        embedding = json.loads(row[1])
        known_face_names.append(name)
        known_face_embeddings.append(np.array(embedding))
        
    conn.close()
    
    # Outcome: Returns two lists: one of embeddings and one of names.
    return known_face_embeddings, known_face_names

# ==============================================================================
# SECTION 3: SYSTEM INITIALIZATION
# ==============================================================================
# Task: Load user data into memory, initialize the camera, and set state variables.
known_face_embeddings, known_face_names = load_known_faces()
cap = cv2.VideoCapture(0)

blink_counter = 0
liveness_verified = False
liveness_status_text = "Please Blink to Verify"

print("System Initialized. Starting camera...")

# ==============================================================================
# SECTION 4: MAIN APPLICATION LOOP
# ==============================================================================
while cap.isOpened():
    # Task: Read one frame from the camera feed.
    ret, frame = cap.read()
    if not ret:
        break

    # --- 4.1: LIVENESS CHECK ---
    # Task: Use the vision_utils module to check for a blink in the current frame.
    """
    # Module         : vision_utils.py
    # Description    : Contains all logic for blink detection (liveness).
    # Author         : Himanshu
    """
    is_live, new_blink_counter = vutils.check_blink(frame, blink_counter)
    blink_counter = new_blink_counter
    
    if is_live:
        liveness_verified = True
        liveness_status_text = "Liveness Verified!"

    # --- 4.2: FACE RECOGNITION ---
    # Task: If liveness is confirmed, run face recognition on the frame.
    if liveness_verified:
        try:
            live_face_locations = face_recognition.face_locations(frame)
            live_face_embeddings = face_recognition.face_encodings(frame, live_face_locations)

            for i, face_embedding in enumerate(live_face_embeddings):
                # Task: Compare the live face embedding to all known embeddings.
                matches = face_recognition.compare_faces(known_face_embeddings, face_embedding, tolerance=0.6)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_embeddings, face_embedding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        
                        # Task: Reset liveness after a successful recognition.
                        liveness_verified = False 
                        liveness_status_text = "Verified! Please Blink Again"

                # Task: Draw visual feedback (bounding box and name) on the frame.
                top, right, bottom, left = live_face_locations[i]
                box_color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)
        
        except Exception as e:
            print(f"An error occurred during face recognition: {e}")

    # --- 4.3: DISPLAY OUTPUT ---
    # Task: Display the liveness status and the final processed frame.
    cv2.putText(frame, liveness_status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow('Smart Attendance System', frame)

    # Task: Check for the 'q' key to exit the loop.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==============================================================================
# SECTION 5: CLEANUP
# ==============================================================================
# Task: Release camera resources and close all GUI windows.
cap.release()
cv2.destroyAllWindows()
