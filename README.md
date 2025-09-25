# Smart Attendance System

A high-performance facial recognition attendance system built with Python and OpenCV. This project uses computer vision and machine learning to provide secure, automated attendance tracking with liveness detection to prevent spoofing.

## Overview

This project provides an end-to-end solution for automated attendance management using facial recognition technology. The system combines a user-friendly graphical interface with advanced computer vision algorithms to deliver accurate and secure attendance tracking. With features like blink detection for liveness verification and real-time facial landmark guidance, the system achieves high accuracy in user identification while preventing fraudulent attendance attempts.

## Technologies Used

* **Python 3.8+**
* **TKinter**
* **Core Libraries:**
    * **OpenCV:** For computer vision operations and video processing.
    * **Face Recognition:** For facial feature detection and encoding.
    * **SQLite3:** For database management and user storage.
    * **Pillow (PIL):** For image processing and display.
    * **NumPy:** For numerical operations and array processing.

## Features

**High-Accuracy Recognition:** Utilizes advanced facial encoding algorithms for reliable user identification.

**Liveness Detection:** Implements blink detection using eye aspect ratio (EAR) to prevent spoofing with photographs.

**Real-time Feedback:** Provides visual guidance through facial landmark detection during enrollment and verification.

**Automated Attendance Logging:** Records attendance with timestamps and exports to CSV for easy reporting.

**User-Friendly Interface:** Clean, professional GUI with intuitive navigation and consistent styling.

**Database Management:** Efficient storage and retrieval of user data and facial encodings using SQLite.

**Cross-Platform Compatibility:** Works on Windows, macOS, and Linux systems.

## Methodology & Pipeline

The project follows a structured workflow for both enrollment and attendance marking:

<img width="3183" height="2889" alt="DFD" src="https://github.com/user-attachments/assets/207606d8-a49f-4334-b372-9d2987228a86" />


**System Initialization:** Loading required libraries and initializing the database connection.

**User Enrollment:**
* Capture facial image through webcam
* Detect facial landmarks and generate encodings
* Store user data with unique UUID in database

**Attendance Verification:**
* Continuous video capture for face detection
* Facial encoding generation and database matching
* Liveness verification through blink detection
* Attendance logging with timestamp

**Data Export:** Automatic CSV generation of attendance records for reporting.


## Performance & Results

The system demonstrates high reliability in both enrollment and verification processes:

| **Metric** | **Performance** |
|------------|-----------------|
| **Face Detection Accuracy** | High (with proper lighting conditions) |
| **Liveness Detection Reliability** | Effective against photo spoofing |
| **Verification Speed** | Near real-time (depends on hardware) |
| **Database Efficiency** | Fast retrieval even with large user bases |

## Output

### Home Screen
<img width="1920" height="1020" alt="v2_1" src="https://github.com/user-attachments/assets/75a3302c-bb4a-443b-a74c-58ae94ec28a2" />

*(The home screen shows two options to users for enrolling in the system and marking attendance.)*

### Enrollment Interface
<img width="1920" height="1020" alt="v2_2(u)" src="https://github.com/user-attachments/assets/060096fd-b4c5-4dc8-b901-0372815e4d80" />

<img width="447" height="190" alt="v2_5" src="https://github.com/user-attachments/assets/0d2edc23-b810-41a9-a324-284989a09e06" />


*(The enrollment screen shows real-time facial landmark detection and guides users for optimal positioning.)*

### Attendance Verification
<img width="1920" height="1020" alt="v2_7(u)" src="https://github.com/user-attachments/assets/c4f1c474-2f45-47f0-a74b-d852e7b1eb59" />

<img width="367" height="190" alt="v2_8" src="https://github.com/user-attachments/assets/53a0cf53-b6fa-462b-b339-ec437496e220" />

*(The attendance interface provides visual feedback during the verification process with progress indicators.)*


### Attendance Report
*(Sample CSV output showing attendance records with timestamps and user details.)*
```csv
Sr No	User ID	Username	Status	Timestamp
1	dbb19b77-28c3-444f-be50-f7876c8a6334	ashish	Present	30-08-2025 16:58
2	3ed0970d-9f73-40cd-a04e-2183a2078083	Chaitanya Khot	Present	30-08-2025 17:43
3	2d6e5913-2a35-4f0f-8f90-026991d50d5a	Chaitanya Khot	Present	02-09-2025 00:25
```

## Conclusion

This project successfully demonstrates a practical application of facial recognition technology for attendance management. By combining accurate facial encoding with liveness detection, the system provides a secure and efficient alternative to traditional attendance methods. The intuitive interface makes it accessible for various environments including educational institutions, corporate offices, and events.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/KhotChaitanya/AI-Powered-Eye-Sensor-Attendance-System.git
    cd AI-Powered-Eye-Sensor-Attendance-System
    ```

2.  **Create a virtual environment (recommended):**
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Run the application:**
    ```sh
    python main_gui.py
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
