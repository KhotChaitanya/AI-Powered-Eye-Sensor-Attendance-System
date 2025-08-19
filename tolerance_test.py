import face_recognition
import os

def run_tolerance_test():
    # Define your image paths
    known_images = {
        "Himanshu1": "test_images/himanshu1.jpg",
        "Himanshu2": "test_images/himanshu2.jpg"
    }

    test_images = {
        "Unknown1": "test_images/unknown1.jpg",
        "Unknown2": "test_images/unknown2.jpg"
    }

    # Encode known images
    known_encodings = {}
    for name, path in known_images.items():
        if os.path.exists(path):
            img = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(img)
            if encodings:
                known_encodings[name] = encodings[0]
                print(f"Encoded {name} from {path}")
            else:
                print(f" No face found in {path}")
        else:
            print(f" File not found: {path}")

    print("\n---- Testing Faces ----\n")

    # Compare with test images
    for test_name, path in test_images.items():
        if os.path.exists(path):
            img = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(img)

            if encodings:
                test_encoding = encodings[0]
                for known_name, known_encoding in known_encodings.items():
                    distance = face_recognition.face_distance([known_encoding], test_encoding)[0]
                    result = face_recognition.compare_faces([known_encoding], test_encoding, tolerance=0.6)[0]
                    print(f" {test_name} vs {known_name} -> Match: {result}, Distance: {distance:.4f}")
            else:
                print(f" No face found in {path}")
        else:
            print(f" File not found: {path}")

if __name__ == "__main__":
    run_tolerance_test()
