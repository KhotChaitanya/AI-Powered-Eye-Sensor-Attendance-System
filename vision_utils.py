# vision_utils.py

import math
import mediapipe as mp

# Initialize MediaPipe components
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# Liveness detection constants
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
EAR_THRESHOLD = 0.25
BLINK_FRAMES_MIN = 2
BLINK_FRAMES_MAX = 5

# Helper function to calculate distance
def _euclidean_distance(point1, point2):
    return math.dist(point1, point2)

# Helper function to calculate Eye Aspect Ratio (EAR)
def _calculate_ear(landmarks, eye_indices):
    v1 = _euclidean_distance(landmarks[eye_indices[1]], landmarks[eye_indices[5]])
    v2 = _euclidean_distance(landmarks[eye_indices[2]], landmarks[eye_indices[4]])
    h = _euclidean_distance(landmarks[eye_indices[0]], landmarks[eye_indices[3]])
    
    # --- BUG FIX ---
    # Added a check to prevent division by zero
    if h == 0:
        return 0.0
        
    ear = (v1 + v2) / (2.0 * h)
    return ear

# Main function for blink detection
def check_blink(frame, blink_counter):
    is_live = False
    
    # Process the frame with MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape
            landmarks = [(lm.x * w, lm.y * h) for lm in face_landmarks.landmark]

            left_ear = _calculate_ear(landmarks, LEFT_EYE)
            right_ear = _calculate_ear(landmarks, RIGHT_EYE)
            ear = (left_ear + right_ear) / 2.0

            if ear < EAR_THRESHOLD:
                blink_counter += 1
            else:
                if BLINK_FRAMES_MIN <= blink_counter <= BLINK_FRAMES_MAX:
                    is_live = True
                blink_counter = 0
    else:
        # If no face is detected, reset the counter
        blink_counter = 0

    return is_live, blink_counter