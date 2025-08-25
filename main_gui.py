"""
File name      : main_gui.py
Description    : The main graphical user interface for the Smart Attendance System.
                 This is the single entry point for the entire application.
Author         : Ragini (UI Design)
Contributor    : Chaitanya (Backend Integration)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import time
import backend # Import the unified backend

# ==============================================================================
# SECTION 1: ENROLLMENT WINDOW
# ==============================================================================
class EnrollmentApp(tk.Toplevel):
    def __init__(self, master, backend_system):
        """
        Function name  : __init__
        Description    : Initializes the enrollment window and its widgets.
        Author         : Ragini
        """
        super().__init__(master)
        self.backend = backend_system # Store a reference to the backend
        self.title("Smart Attendance - Enroll New User")
        self.geometry("600x550")
        self.configure(bg="#f3f6f7")

        # --- Widgets ---
        tk.Label(self, text="Enroll New User", font=("Segoe UI", 18, "bold"), bg="#f3f6f7").pack(pady=10)
        self.video_frame = tk.Label(self, bg="#d0dedc")
        self.video_frame.pack(padx=20, pady=10)
        
        entry_frame = tk.Frame(self, bg="#f3f6f7")
        entry_frame.pack(pady=10)
        tk.Label(entry_frame, text="Full Name:", font=("Segoe UI", 12), bg="#f3f6f7").grid(row=0, column=0, padx=5)
        self.name_entry = tk.Entry(entry_frame, font=("Segoe UI", 12), width=30)
        self.name_entry.grid(row=0, column=1, padx=5)

        btn_frame = tk.Frame(self, bg="#f3f6f7")
        btn_frame.pack(pady=15)
        self.btn_save = ttk.Button(btn_frame, text="Capture & Enroll", command=self.save_user)
        self.btn_save.grid(row=0, column=0, padx=10)
        self.btn_close = ttk.Button(btn_frame, text="Close", command=self.close_window)
        self.btn_close.grid(row=0, column=1, padx=10)

        # --- Camera Setup ---
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.captured_frame = None
        self.update_video()

    def update_video(self):
        """
        Function name  : update_video
        Description    : Continuously captures and displays the camera feed.
        Author         : Ragini
        """
        if not self.running: return
        ret, frame = self.cap.read()
        if ret:
            self.captured_frame = frame.copy()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image).resize((480, 360))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
        self.after(15, self.update_video)

    def save_user(self):
        """
        Function name  : save_user
        Description    : Handles the logic for enrolling a new user by calling the backend.
        Author         : Ragini
        Modified by    : Chaitanya (for backend integration)
        """
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name!")
            return
        
        # ----------------------------------------------------------------------
        """
        # INTEGRATION POINT: Call the backend to enroll the user.
        # Author: Chaitanya
        """
        # ----------------------------------------------------------------------
        success, message = self.backend.add_user(name, self.captured_frame)
        if success:
            messagebox.showinfo("Success", message)
            self.close_window()
        else:
            messagebox.showerror("Error", message)

    def close_window(self):
        """
        Function name  : close_window
        Description    : Safely releases the camera and closes the window.
        Author         : Ragini
        """
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

# ==============================================================================
# SECTION 2: MARK ATTENDANCE WINDOW
# ==============================================================================
class MarkAttendanceApp(tk.Toplevel):
    def __init__(self, master, backend_system):
        """
        Function name  : __init__
        Description    : Initializes the attendance marking window and its widgets.
        Author         : Ragini
        """
        super().__init__(master)
        self.backend = backend_system
        self.title("Smart Attendance - Mark Attendance")
        self.geometry("600x550")
        self.configure(bg="#f3f6f7")
        
        # --- Widgets ---
        tk.Label(self, text="Mark Attendance", font=("Segoe UI", 18, "bold"), bg="#f3f6f7").pack(pady=10)
        self.video_frame = tk.Label(self, bg="#d0dedc")
        self.video_frame.pack(padx=20, pady=10)
        self.status_label = tk.Label(self, text="Status: Initializing...", font=("Segoe UI", 14, "italic"), bg="#f3f6f7")
        self.status_label.pack(pady=10)
        self.btn_close = ttk.Button(self, text="Close", command=self.close_window)
        self.btn_close.pack(pady=10)

        # --- Camera Setup ---
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.update_video()

    def update_video(self):
        """
        Function name  : update_video
        Description    : Main loop for the attendance screen. Calls the backend
                         and updates the UI with the latest status.
        Author         : Ragini
        Modified by    : Chaitanya (for backend integration)
        """
        if not self.running: return
        ret, frame = self.cap.read()
        if ret:
            # ----------------------------------------------------------------------
            # INTEGRATION POINT: Call the backend's main workflow function.
            # Author: Chaitanya
            # ----------------------------------------------------------------------
            status_msg, status_color_bgr = self.backend.run_attendance_check(frame)
            
            # Update the on-screen text and color
            self.status_label.config(text=f"Status: {status_msg}")
            
            # Draw overlay on the frame
            cv2.putText(frame, status_msg, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color_bgr, 2)
            
            # Convert for Tkinter
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image).resize((480, 360))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
            
        self.after(15, self.update_video)

    def close_window(self):
        """
        Function name  : close_window
        Description    : Safely releases the camera and closes the window.
        Author         : Ragini
        """
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

# ==============================================================================
# SECTION 3: MAIN HOME PAGE
# ==============================================================================
class HomePage(tk.Tk):
    def __init__(self, backend_system):
        """
        Function name  : __init__
        Description    : Initializes the main home page of the application.
        Author         : Ragini
        """
        super().__init__()
        self.backend_system = backend_system
        self.title("Smart Attendance System")
        self.geometry("700x400")
        self.configure(bg="#f3f6f7")
        
        # --- Widgets ---
        tk.Label(self, text="Smart Attendance System", font=("Segoe UI", 24, "bold"), bg="#f3f6f7").pack(pady=20)
        tk.Label(self, text="Welcome to the main hub. Please choose an option below.", font=("Segoe UI", 12), bg="#f3f6f7").pack(pady=10)
        
        card_frame = tk.Frame(self, bg="#f3f6f7")
        card_frame.pack(pady=30, expand=True, fill="both")
        
        # --- Enrollment Card ---
        enroll_card = tk.Frame(card_frame, bg="white", relief="raised", bd=2, cursor="hand2")
        enroll_card.pack(side="left", padx=40, pady=20, expand=True, fill="both")
        enroll_icon = tk.Label(enroll_card, text="🧑‍💼", font=("Segoe UI", 50), bg="white")
        enroll_icon.pack(pady=(10,0))
        enroll_title = tk.Label(enroll_card, text="Enroll User", font=("Segoe UI", 16, "bold"), bg="white")
        enroll_title.pack(pady=5)
        ttk.Button(enroll_card, text="Launch Enrollment", command=self.open_enrollment).pack(pady=15)
        enroll_card.bind("<Button-1>", lambda e: self.open_enrollment())
        enroll_icon.bind("<Button-1>", lambda e: self.open_enrollment())
        enroll_title.bind("<Button-1>", lambda e: self.open_enrollment())

        # --- Attendance Card ---
        attendance_card = tk.Frame(card_frame, bg="white", relief="raised", bd=2, cursor="hand2")
        attendance_card.pack(side="right", padx=40, pady=20, expand=True, fill="both")
        attendance_icon = tk.Label(attendance_card, text="✅", font=("Segoe UI", 50), bg="white")
        attendance_icon.pack(pady=(10,0))
        attendance_title = tk.Label(attendance_card, text="Mark Attendance", font=("Segoe UI", 16, "bold"), bg="white")
        attendance_title.pack(pady=5)
        ttk.Button(attendance_card, text="Launch Attendance", command=self.open_mark_attendance).pack(pady=15)
        attendance_card.bind("<Button-1>", lambda e: self.open_mark_attendance())
        attendance_icon.bind("<Button-1>", lambda e: self.open_mark_attendance())
        attendance_title.bind("<Button-1>", lambda e: self.open_mark_attendance())

    def open_enrollment(self):
        EnrollmentApp(self, self.backend_system)

    def open_mark_attendance(self):
        MarkAttendanceApp(self, self.backend_system)

# ==============================================================================
# SECTION 4: MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    # --- Initialize backend BEFORE the GUI to prevent blocking ---
    print("Initializing backend system...")
    system_backend = backend.AttendanceSystem()
    print("Launching GUI...")
    
    app = HomePage(backend_system=system_backend)
    app.mainloop()

