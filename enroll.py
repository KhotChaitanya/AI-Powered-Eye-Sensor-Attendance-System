import cv2
import face_recognition
import database as db


user_name = input("Enter the name of the new user: ")

cap = cv2.VideoCapture(0)
print("Camera opened. Look at the camera and press 's' to save your picture.")
print("Press 'q' to quit without saving.")

while True:
    # Read one frame from the camera.
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
        
    # Display the live video feed in a window.
    cv2.imshow("Enrollment - Press 's' to save, 'q' to quit", frame)

    # Wait for a key press.
    key = cv2.waitKey(1) & 0xFF

    # If the 's' key is pressed, save the photo and process it.
    if key == ord('s'):
        # Use the face_recognition library to find faces in the current frame.
        face_locations = face_recognition.face_locations(frame)
        
        # Check if exactly one face was found.
        if len(face_locations) == 1:
            # Get the face embedding for the found face.
            # The [0] is used because face_encodings returns a list, and we want the first (and only) item.
            embedding = face_recognition.face_encodings(frame, face_locations)[0]
            
            # Convert the embedding from a NumPy array to a regular Python list so we can save it.
            embedding_list = embedding.tolist()
            
            # Add the new user to our database.
            db.add_user(user_name, embedding_list)
            
            # Break the loop since we are done.
            break
        elif len(face_locations) > 1:
            print("Error: More than one face detected. Please ensure only one person is in the frame.")
        else:
            print("Error: No face detected. Please look directly at the camera.")

    # If the 'q' key is pressed, quit the program.
    elif key == ord('q'):
        print("Enrollment cancelled.")
        break

# --- Clean Up ---
# Release the camera and close all OpenCV windows.
cap.release()
cv2.destroyAllWindows()