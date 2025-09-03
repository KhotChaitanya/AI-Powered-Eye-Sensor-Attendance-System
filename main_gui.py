"""
File name      : main_gui.py
Description    : The main graphical user interface for the Smart Attendance System.
                 This is the single entry point for the entire application.
Author         : Ragini (UI/UX Design)
Co-author      : Chaitanya (Refactoring & Integration)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import time
import backend
import tkinter.font as tkFont
import face_recognition

# ==============================================================================
# SECTION 0: CONSTANTS AND STYLES
# ==============================================================================
"""
Function name  : COLORS, FONTS (constants)
Description    : Defines the color palette and font styles for the entire application.
                 This provides a consistent visual design system.
Author         : Chaitanya
"""
COLORS = {
    "primary": "#2563eb",      # Vibrant blue
    "secondary": "#f59e0b",    # Amber
    "accent": "#10b981",       # Emerald
    "background": "#f8fafc",   # Light gray
    "surface": "#ffffff",      # White
    "text": "#1e293b",         # Dark gray
    "text_light": "#64748b",   # Medium gray
    "error": "#ef4444",        # Red
    "success": "#10b981",      # Green
    "warning": "#f59e0b"       # Amber
}

FONTS = {
    "title": ("Segoe UI", 24, "bold"),
    "subtitle": ("Segoe UI", 16),
    "body": ("Segoe UI", 12),
    "button": ("Segoe UI", 12, "bold")
}

# ==============================================================================
# SECTION 1: ENROLLMENT WINDOW
# ==============================================================================
class EnrollmentApp(tk.Toplevel):
    def __init__(self, master, backend_system):
        """
        Function name  : __init__
        Description    : Initializes the Enrollment window with navigation, video feed, and form.
        Author         : Ragini (UI/UX Design)
        Co-author      : Chaitanya (Functional Logic & Integration)
        """
        super().__init__(master)
        self.backend = backend_system
        self.title("Smart Attendance - Enroll New User")
        self.configure(bg=COLORS["background"])
        self.state('zoomed')

        # Navigation Bar
        nav_frame = tk.Frame(self, bg=COLORS["primary"], height=60)
        nav_frame.pack(fill="x")
        nav_frame.pack_propagate(False)
        
        tk.Label(nav_frame, text="Smart Attendance System", font=("Segoe UI", 16, "bold"), 
                bg=COLORS["primary"], fg="white").pack(side="left", padx=20)
        
        nav_buttons = tk.Frame(nav_frame, bg=COLORS["primary"])
        nav_buttons.pack(side="right", padx=20)
        
        home_btn = tk.Button(nav_buttons, text="Home", font=("Segoe UI", 12), 
                            bg=COLORS["primary"], fg="white", bd=0, cursor="hand2",
                            command=self.master.deiconify)
        home_btn.pack(side="left", padx=10)
        home_btn.bind("<Enter>", lambda e: home_btn.config(bg=COLORS["secondary"]))
        home_btn.bind("<Leave>", lambda e: home_btn.config(bg=COLORS["primary"]))
        
        close_btn = tk.Button(nav_buttons, text="Close", font=("Segoe UI", 12), 
                             bg=COLORS["primary"], fg="white", bd=0, cursor="hand2",
                             command=self.close_window)
        close_btn.pack(side="left", padx=10)
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=COLORS["secondary"]))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=COLORS["primary"]))
        
        # Header
        header_frame = tk.Frame(self, bg="#dbeafe", height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Enroll New User", font=("Segoe UI", 24, "bold"), 
                bg="#dbeafe", fg="#1e40af").pack(expand=True)
        
        tk.Label(header_frame, text="Register a new user in the system", 
                font=("Segoe UI", 14), bg="#dbeafe", fg="#3b82f6").pack(expand=True)
        
        # Main content
        content_frame = tk.Frame(self, bg=COLORS["background"])
        content_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Left side - Video feed
        video_container = tk.Frame(content_frame, bg=COLORS["background"])
        video_container.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        video_header = tk.Frame(video_container, bg=COLORS["background"])
        video_header.pack(fill="x", pady=(0, 10))
        
        tk.Label(video_header, text="Camera Feed", font=("Segoe UI", 16, "bold"), 
                bg=COLORS["background"], fg=COLORS["text"]).pack(side="left")
        
        self.video_frame = tk.Label(video_container, bg="#e2e8f0", bd=2, relief='sunken')
        self.video_frame.pack(pady=10)
        
        # Right side - Form
        form_container = tk.Frame(content_frame, bg=COLORS["background"])
        form_container.pack(side="right", fill="both", expand=True, padx=(20, 0))
        
        form_header = tk.Frame(form_container, bg=COLORS["background"])
        form_header.pack(fill="x", pady=(0, 20))
        
        tk.Label(form_header, text="User Details", font=("Segoe UI", 16, "bold"), 
                bg=COLORS["background"], fg=COLORS["text"]).pack(side="left")
        
        form = tk.Frame(form_container, bg=COLORS["surface"], padx=20, pady=20, relief="raised", bd=1)
        form.pack(fill="both", expand=True)
        
        tk.Label(form, text="Full Name:", font=("Segoe UI", 14), 
                bg=COLORS["surface"], fg=COLORS["text"], anchor="w").pack(fill="x", pady=10)
        
        self.name_entry = tk.Entry(form, font=("Segoe UI", 14), width=30)
        self.name_entry.pack(fill="x", pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(form, bg=COLORS["surface"])
        btn_frame.pack(pady=30)
        
        self.btn_save = tk.Button(btn_frame, text="Capture & Enroll", command=self.start_enrollment_process)
        self.btn_save.grid(row=0, column=0, padx=15)
        
        self.btn_close = tk.Button(btn_frame, text="Close", command=self.close_window)
        self.btn_close.grid(row=0, column=1, padx=15)
        
        self.style_buttons(btn_frame)

        # Initialize video
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.captured_frame = None
        self.countdown = 3
        self.countdown_running = False
        self.update_video()

    def style_buttons(self, widget):
        """
        Function name  : style_buttons
        Description    : Applies consistent styling to all buttons in the given widget.
        Author         : Ragini
        """
        for child in widget.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(bg=COLORS["primary"], fg="white", 
                               activebackground=COLORS["secondary"], 
                               activeforeground="white", font=("Segoe UI", 13, "bold"), 
                               bd=0, relief="flat", padx=24, pady=10, cursor="hand2")
                child.bind("<Enter>", lambda e, b=child: b.config(bg=COLORS["secondary"]))
                child.bind("<Leave>", lambda e, b=child: b.config(bg=COLORS["primary"]))
            elif isinstance(child, tk.Frame):
                self.style_buttons(child)

    def draw_dynamic_guides(self, frame, face_landmarks_list):
        """
        Function name  : draw_dynamic_guides
        Description    : Draws facial landmarks and guidance text on the video frame.
        Author         : Chaitanya
        """
        if not face_landmarks_list:
            cv2.putText(frame, "Align Face in View", (50, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
        for face_landmarks in face_landmarks_list:
            # Draw eye landmarks
            if "left_eye" in face_landmarks:
                for point in face_landmarks['left_eye']:
                    cv2.circle(frame, point, 2, (0, 255, 0), -1)
            if "right_eye" in face_landmarks:
                for point in face_landmarks['right_eye']:
                    cv2.circle(frame, point, 2, (0, 255, 0), -1)
            # Draw face outline (chin)
            if "chin" in face_landmarks:
                points = face_landmarks['chin']
                for i in range(len(points) - 1):
                    cv2.line(frame, points[i], points[i+1], (0, 255, 0), 2)
        return frame

    def update_video(self):
        """
        Function name  : update_video
        Description    : Continuously updates the video feed with facial guides and countdown.
        Author         : Chaitanya
        """
        if not self.running: 
            return
        ret, frame = self.cap.read()
        if ret:
            face_landmarks_list = face_recognition.face_landmarks(frame)
            frame = self.draw_dynamic_guides(frame, face_landmarks_list)
            if self.countdown_running:
                text = f"Capturing in {self.countdown}..."
                cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3, cv2.LINE_AA)
            self.captured_frame = frame.copy()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image).resize((640, 480))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
        self.after(30, self.update_video)

    def start_enrollment_process(self):
        """
        Function name  : start_enrollment_process
        Description    : Validates input and initiates the enrollment countdown.
        Author         : Chaitanya
        """
        if self.countdown_running: 
            return
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name!")
            return
        self.countdown_running = True
        self.countdown = 3
        self._do_countdown()

    def _do_countdown(self):
        """
        Function name  : _do_countdown
        Description    : Handles the countdown timer before capturing the image.
        Author         : Chaitanya
        """
        if self.countdown > 0:
            self.countdown -= 1
            self.after(1000, self._do_countdown)
        else:
            self.countdown_running = False
            success, message = self.backend.add_user(self.name_entry.get().strip(), self.captured_frame)
            if success:
                # Show the success message with the unique ID
                messagebox.showinfo("Success", message)
                self.close_window()
            else:
                messagebox.showerror("Error", message)

    def close_window(self):
        """
        Function name  : close_window
        Description    : Safely releases camera resources and closes the window.
        Author         : Chaitanya
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
        Description    : Initializes the Mark Attendance window with video feed and status panel.
        Author         : Ragini (UI/UX Design)
        Co-author      : Chaitanya (Functional Logic & Integration)
        """
        super().__init__(master)
        self.backend = backend_system
        self.title("Smart Attendance - Mark Attendance")
        self.configure(bg=COLORS["background"])
        self.state('zoomed')

        # Navigation Bar
        nav_frame = tk.Frame(self, bg=COLORS["primary"], height=60)
        nav_frame.pack(fill="x")
        nav_frame.pack_propagate(False)
        
        tk.Label(nav_frame, text="Smart Attendance System", font=("Segoe UI", 16, "bold"), 
                bg=COLORS["primary"], fg="white").pack(side="left", padx=20)
        
        nav_buttons = tk.Frame(nav_frame, bg=COLORS["primary"])
        nav_buttons.pack(side="right", padx=20)
        
        close_btn = tk.Button(nav_buttons, text="Close", font=("Segoe UI", 12), 
                             bg=COLORS["primary"], fg="white", bd=0, cursor="hand2",
                             command=self.close_window)
        close_btn.pack(side="left", padx=10)
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=COLORS["secondary"]))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=COLORS["primary"]))
        
        # Header
        header_frame = tk.Frame(self, bg="#dbeafe", height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Mark Attendance", font=("Segoe UI", 24, "bold"), 
                bg="#dbeafe", fg="#1e40af").pack(expand=True)
        
        tk.Label(header_frame, text="Record attendance using facial recognition", 
                font=("Segoe UI", 14), bg="#dbeafe", fg="#3b82f6").pack(expand=True)
        
        # Main content - Two-column layout
        content_frame = tk.Frame(self, bg=COLORS["background"])
        content_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Left side - Video feed
        video_container = tk.Frame(content_frame, bg=COLORS["background"])
        video_container.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        video_header = tk.Frame(video_container, bg=COLORS["background"])
        video_header.pack(fill="x", pady=(0, 10))
        
        tk.Label(video_header, text="Camera Feed", font=("Segoe UI", 16, "bold"), 
                bg=COLORS["background"], fg=COLORS["text"]).pack(side="left")
        
        self.video_frame = tk.Label(video_container, bg="#e2e8f0", bd=2, relief='sunken')
        self.video_frame.pack(pady=10)
        
        # Right side - Status and controls
        status_container = tk.Frame(content_frame, bg=COLORS["background"])
        status_container.pack(side="right", fill="both", expand=True, padx=(20, 0))
        
        status_header = tk.Frame(status_container, bg=COLORS["background"])
        status_header.pack(fill="x", pady=(0, 20))
        
        tk.Label(status_header, text="Attendance Status", font=("Segoe UI", 16, "bold"), 
                bg=COLORS["background"], fg=COLORS["text"]).pack(side="left")
        
        # Status panel with improved styling
        status_panel = tk.Frame(status_container, bg=COLORS["surface"], padx=20, pady=20, relief="raised", bd=1)
        status_panel.pack(fill="both", expand=True)
        
        # Status label
        self.status_label = tk.Label(status_panel, text="Status: Initializing...", 
                                   font=("Segoe UI", 15, "italic"), bg=COLORS["surface"], fg="#495f88")
        self.status_label.pack(pady=(20, 10), anchor="w")
        
        # Progress bar with label
        progress_frame = tk.Frame(status_panel, bg=COLORS["surface"])
        progress_frame.pack(fill="x", pady=(20, 10))
        
        tk.Label(progress_frame, text="Verification Progress:", font=("Segoe UI", 12), 
                bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(5, 0))
        
        # Instructions
        instructions_frame = tk.Frame(status_panel, bg=COLORS["surface"])
        instructions_frame.pack(fill="x", pady=(30, 10))
        
        tk.Label(instructions_frame, text="Instructions:", font=("Segoe UI", 12, "bold"), 
                bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        
        instructions = [
            "1. Position your face in the camera view",
            "2. Keep still until verification completes",
            "3. Attendance will be automatically recorded"
        ]
        
        for instruction in instructions:
            tk.Label(instructions_frame, text=instruction, font=("Segoe UI", 10), 
                    bg=COLORS["surface"], fg=COLORS["text_light"], justify="left").pack(anchor="w", pady=(5, 0))
        
        # Close button
        self.btn_close = tk.Button(status_panel, text="Close", command=self.close_window)
        self.btn_close.pack(pady=(30, 10))
        self.style_buttons(status_panel)

        # Initialize video
        self.cap = cv2.VideoCapture(0)
        self.running = True
        
        # Reset backend state when opening the window
        self.backend.reset_workflow()
        
        # Check if there are enrolled users
        if not self.backend.has_enrolled_users():
            messagebox.showerror("Error", "No users enrolled. Please enroll at least one user before marking attendance.")
            self.close_window()
            return
        
        self.update_video()

    def style_buttons(self, widget):
        """
        Function name  : style_buttons
        Description    : Applies consistent styling to all buttons in the given widget.
        Author         : Ragini
        """
        for child in widget.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(bg=COLORS["primary"], fg="white", 
                               activebackground=COLORS["secondary"], 
                               activeforeground="white", font=("Segoe UI", 13, "bold"), 
                               bd=0, relief="flat", padx=24, pady=10, cursor="hand2")
                child.bind("<Enter>", lambda e, b=child: b.config(bg=COLORS["secondary"]))
                child.bind("<Leave>", lambda e, b=child: b.config(bg=COLORS["primary"]))
            elif isinstance(child, tk.Frame):
                self.style_buttons(child)

    def draw_dynamic_guides(self, frame, face_landmarks_list):
        """
        Function name  : draw_dynamic_guides
        Description    : Draws facial landmarks and guidance text on the video frame.
        Author         : Chaitanya
        """
        if not face_landmarks_list:
             cv2.putText(frame, "Align Face in View", (50, frame.shape[0] - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
        for face_landmarks in face_landmarks_list:
            # Draw eye landmarks
            if "left_eye" in face_landmarks:
                for point in face_landmarks['left_eye']:
                    cv2.circle(frame, point, 2, (0, 255, 0), -1)
            if "right_eye" in face_landmarks:
                for point in face_landmarks['right_eye']:
                    cv2.circle(frame, point, 2, (0, 255, 0), -1)
            # Draw face outline (chin)
            if "chin" in face_landmarks:
                points = face_landmarks['chin']
                for i in range(len(points) - 1):
                    cv2.line(frame, points[i], points[i+1], (0, 255, 0), 2)
        return frame

    def update_video(self):
        """
        Function name  : update_video
        Description    : Continuously updates the video feed and processes attendance marking.
        Author         : Chaitanya
        """
        if not self.running: 
            return
        ret, frame = self.cap.read()
        if ret:
            face_landmarks_list = face_recognition.face_landmarks(frame)
            status_msg, status_color_bgr, progress = self.backend.run_attendance_check(frame, face_landmarks_list)
            frame = self.draw_dynamic_guides(frame, face_landmarks_list)
            
            cv2.putText(frame, status_msg, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color_bgr, 3, cv2.LINE_AA)
            self.status_label.config(text=f"Status: {status_msg}", fg="#2a4365")
            self.progress_bar['value'] = progress
            
            # Force GUI update to ensure progress bar is visible
            self.update_idletasks()
            
            # Check for final success state
            if self.backend.workflow_state == "FINAL_SUCCESS":
                self.running = False
                messagebox.showinfo("Success", f"Attendance Marked for {self.backend.pending_verification_user['name']}")
                # Reset backend state for next use
                self.backend.reset_workflow()
                self.close_window()
                return

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image).resize((640, 480))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
        self.after(30, self.update_video)

    def close_window(self):
        """
        Function name  : close_window
        Description    : Safely releases camera resources and closes the window.
        Author         : Chaitanya
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
        Description    : Initializes the main home page with navigation cards.
        Author         : Ragini (UI/UX Design)
        Co-author      : Chaitanya (Functional Logic & Integration)
        """
        super().__init__()
        self.backend_system = backend_system
        self.title("Smart Attendance System")
        self.configure(bg=COLORS["background"])
        self.state('zoomed')
        
        # Header
        header_frame = tk.Frame(self, bg=COLORS["primary"], height=120)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Smart Attendance System", 
                font=("Segoe UI", 28, "bold"), bg=COLORS["primary"], fg="white").pack(expand=True, pady=(10, 0))
        
        tk.Label(header_frame, text="Facial Recognition Attendance Management", 
                font=("Segoe UI", 16), bg=COLORS["primary"], fg="#dbeafe").pack(expand=True, pady=(0, 10))
        
        # Main content
        content_frame = tk.Frame(self, bg=COLORS["background"])
        content_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Cards container
        cards_frame = tk.Frame(content_frame, bg=COLORS["background"])
        cards_frame.pack(expand=True)
        
        # Enrollment card
        enroll_card = tk.Frame(cards_frame, bg=COLORS["surface"], relief="raised", bd=1, width=300, height=400)
        enroll_card.grid(row=0, column=0, padx=40, pady=20, sticky="nsew")
        enroll_card.pack_propagate(False)
        
        tk.Label(enroll_card, text="👤", font=("Segoe UI", 48), 
                bg=COLORS["surface"]).pack(pady=(40, 20))
        
        tk.Label(enroll_card, text="Enroll User", font=("Segoe UI", 20, "bold"), 
                bg=COLORS["surface"], fg=COLORS["text"]).pack(pady=(0, 15))
        
        tk.Label(enroll_card, text="Register new users in the system", 
                font=("Segoe UI", 12), bg=COLORS["surface"], fg=COLORS["text_light"], 
                wraplength=250).pack(pady=(0, 30))
        
        enroll_btn = tk.Button(enroll_card, text="Launch Enrollment", font=("Segoe UI", 12, "bold"),
                              bg=COLORS["primary"], fg="white", bd=0, cursor="hand2",
                              command=self.open_enrollment, padx=20, pady=10)
        enroll_btn.pack(pady=20)
        enroll_btn.bind("<Enter>", lambda e: enroll_btn.config(bg=COLORS["secondary"]))
        enroll_btn.bind("<Leave>", lambda e: enroll_btn.config(bg=COLORS["primary"]))
        
        # Attendance card
        attendance_card = tk.Frame(cards_frame, bg=COLORS["surface"], relief="raised", bd=1, width=300, height=400)
        attendance_card.grid(row=0, column=1, padx=40, pady=20, sticky="nsew")
        attendance_card.pack_propagate(False)
        
        tk.Label(attendance_card, text="📋", font=("Segoe UI", 48), 
                bg=COLORS["surface"]).pack(pady=(40, 20))
        
        tk.Label(attendance_card, text="Mark Attendance", font=("Segoe UI", 20, "bold"), 
                bg=COLORS["surface"], fg=COLORS["text"]).pack(pady=(0, 15))
        
        tk.Label(attendance_card, text="Record attendance using facial recognition", 
                font=("Segoe UI", 12), bg=COLORS["surface"], fg=COLORS["text_light"], 
                wraplength=250).pack(pady=(0, 30))
        
        attendance_btn = tk.Button(attendance_card, text="Launch Attendance", font=("Segoe UI", 12, "bold"),
                                  bg=COLORS["primary"], fg="white", bd=0, cursor="hand2",
                                  command=self.open_mark_attendance, padx=20, pady=10)
        attendance_btn.pack(pady=20)
        attendance_btn.bind("<Enter>", lambda e: attendance_btn.config(bg=COLORS["secondary"]))
        attendance_btn.bind("<Leave>", lambda e: attendance_btn.config(bg=COLORS["primary"]))
        
        # Footer
        footer_frame = tk.Frame(content_frame, bg=COLORS["background"])
        footer_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(footer_frame, text="Smart Attendance System • v1.0", 
                font=("Segoe UI", 10), bg=COLORS["background"], fg=COLORS["text_light"]).pack(side="left")
        
        tk.Label(footer_frame, text="Secure • Efficient • Reliable", 
                font=("Segoe UI", 10), bg=COLORS["background"], fg=COLORS["text_light"]).pack(side="right")

    def open_enrollment(self):
        """
        Function name  : open_enrollment
        Description    : Opens the enrollment window.
        Author         : Chaitanya
        """
        EnrollmentApp(self, self.backend_system)

    def open_mark_attendance(self):
        """
        Function name  : open_mark_attendance
        Description    : Opens the attendance marking window after checking for enrolled users.
        Author         : Chaitanya
        """
        # Check if there are any enrolled users before opening the attendance window
        if not self.backend_system.has_enrolled_users():
            messagebox.showerror("Error", "No users enrolled. Please enroll at least one user before marking attendance.")
            return
        MarkAttendanceApp(self, self.backend_system)

# ==============================================================================
# SECTION 4: MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    """
    Function name  : __main__
    Description    : Entry point of the application. Initializes backend and launches GUI.
    Author         : Chaitanya
    """
    print("Initializing backend system...")
    system_backend = backend.AttendanceSystem()
    print("Launching GUI...")
    app = HomePage(backend_system=system_backend)
    app.mainloop()
