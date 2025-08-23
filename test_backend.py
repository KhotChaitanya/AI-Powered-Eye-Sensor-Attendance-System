"""
File name   : test_backend.py
Description : Quick test script for backend.py integration with iris_engine.py
Author      : Himanshu
"""

import cv2
import numpy as np
from backend import AttendanceSystem
from iris_engine import create_iris_code

# Initialize backend
system = AttendanceSystem()

# -----------------------------
# 1. Add a test user (only run once)
# -----------------------------
def add_test_user():
    # Path to eye image of the user
    user_img = "right_iris_clean.jpg"   

    # Generate iris template
    iris_template = create_iris_code(user_img)

    # Dummy face embedding (random vector for now)
    embedding = np.random.rand(128).tolist()

    # Add to database
    system.add_user("Himanshu", embedding, iris_template)


# -----------------------------
# 2. Run recognition on another test image
# -----------------------------
def test_attendance():
    test_img = cv2.imread("right_iris_clean.jpg")   
    if test_img is None:
        print("❌ Test image not found. Place 'sample_eye.jpg' in project folder.")
        return

    status_message, status_color = system.run_attendance_check(test_img)
    print("Status:", status_message, "| Color:", status_color)


if __name__ == "__main__":
    # Step 1: Run once to register user
    add_test_user()

    # Step 2: Run recognition
    test_attendance()
