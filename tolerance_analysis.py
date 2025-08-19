import face_recognition

# Load known images (Himanshu)
himanshu1 = face_recognition.load_image_file("test_images/himanshu1.jpg")
himanshu2 = face_recognition.load_image_file("test_images/himanshu2.jpg")

himanshu1_enc = face_recognition.face_encodings(himanshu1)[0]
himanshu2_enc = face_recognition.face_encodings(himanshu2)[0]

# Load unknown images
unknown1 = face_recognition.load_image_file("test_images/unknown1.jpg")
unknown2 = face_recognition.load_image_file("test_images/unknown2.jpg")

unknown1_enc = face_recognition.face_encodings(unknown1)[0]
unknown2_enc = face_recognition.face_encodings(unknown2)[0]

# Store all comparisons
pairs = [
    ("Unknown1 vs Himanshu1", unknown1_enc, himanshu1_enc),
    ("Unknown1 vs Himanshu2", unknown1_enc, himanshu2_enc),
    ("Unknown2 vs Himanshu1", unknown2_enc, himanshu1_enc),
    ("Unknown2 vs Himanshu2", unknown2_enc, himanshu2_enc),
    ("Himanshu1 vs Himanshu2", himanshu1_enc, himanshu2_enc),  # Same person check
]

# Try different tolerance values
tolerances = [0.5, 0.55, 0.6, 0.65, 0.7]

print("🔎 Face Recognition Tolerance Analysis\n")
for name, enc1, enc2 in pairs:
    distance = face_recognition.face_distance([enc2], enc1)[0]
    results = []
    for tol in tolerances:
        match = distance <= tol
        results.append(f"{'✔' if match else '✘'} (tol={tol})")
    
    print(f"{name} -> Distance: {distance:.4f} | Results: {', '.join(results)}")
