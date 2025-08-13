import cv2
import face_recognition
import sqlite3
import json
import numpy as np

# --- Load Known Faces from Database ---
def load_known_faces():
    known_face_embeddings = []
    known_face_names = []

    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Fetch all users
    cursor.execute("SELECT name, embedding FROM users")
    rows = cursor.fetchall()

    for row in rows:
        name = row[0]
        # The embedding is stored as a JSON string, so we need to convert it back to a list
        embedding = json.loads(row[1])
        
        known_face_names.append(name)
        # The face_recognition library uses NumPy arrays, so we convert the list back
        known_face_embeddings.append(np.array(embedding))

    conn.close()
    print("Loaded known faces from the database.")
    return known_face_embeddings, known_face_names

# --- Initialize ---
known_face_embeddings, known_face_names = load_known_faces()
cap = cv2.VideoCapture(0)

print("Starting camera. Looking for faces...")

while True:
    # --- Read a frame from the camera ---
    ret, frame = cap.read()
    if not ret:
        break

    # --- Find all faces and their embeddings in the current frame ---
    # This is the most resource-intensive part
    live_face_locations = face_recognition.face_locations(frame)
    live_face_embeddings = face_recognition.face_encodings(frame, live_face_locations)

    # --- Loop through each face found in the frame ---
    for i, face_embedding in enumerate(live_face_embeddings):
        
        # This is where the Liveness Check from Himanshu will go later.
        # For now, we assume every detected face is live.

        # --- Compare the live face with all known faces ---
        matches = face_recognition.compare_faces(known_face_embeddings, face_embedding, tolerance=0.6)
        name = "Unknown" # Default name if no match is found

        # Find the best match
        face_distances = face_recognition.face_distance(known_face_embeddings, face_embedding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            
            # This is where the Logging will go later.
            # print(f"Verified: {name}")

        # --- Draw a box and name on the frame ---
        top, right, bottom, left = live_face_locations[i]
        
        # Set box color to green for known faces, red for unknown
        box_color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

        # Draw the box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)

        # Draw a label with the name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # --- Display the final image ---
    cv2.imshow('Smart Attendance System', frame)

    # --- Quit on 'q' key press ---
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Clean Up ---
cap.release()
cv2.destroyAllWindows()