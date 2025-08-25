"""
File name : main_gui.py
Description : The main graphical user interface for the Smart Attendance System.
This is the single entry point for the entire application.
Author : Ragini (UI Design)
Contributor : Chaitanya (Backend Integration)
"""


import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import time
import backend  # Import backend logic
import tkinter.font as tkFont

# Load Haar Cascade for eye detection
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# ----------------- Button Styling -----------------
def style_buttons(widget):
    """Apply consistent style to all Tkinter buttons inside a widget."""
    for child in widget.winfo_children():
        if isinstance(child, tk.Button):
            child.configure(
                bg="#2a4365", fg="white",
                activebackground="#1a2a43", activeforeground="white",
                font=("Segoe UI", 13, "bold"),
                bd=0, relief="flat",
                padx=24, pady=10,
                cursor="hand2"
            )
            # Hover effect
            child.bind("<Enter>", lambda e, b=child: b.config(bg="#1a2a43"))
            child.bind("<Leave>", lambda e, b=child: b.config(bg="#2a4365"))
        elif isinstance(child, tk.Frame):
            style_buttons(child)

# ====================================================================
# ENROLLMENT WINDOW
# ====================================================================
class EnrollmentApp(tk.Toplevel):
    def __init__(self, master, backend_system):
        super().__init__(master)
        self.backend = backend_system
        self.title("Smart Attendance - Enroll New User")
        self.configure(bg="#f0f4f8")
        self.state('zoomed')  # Fullscreen mode

        # Title
        tk.Label(self, text="Enroll New User", font=("Segoe UI", 20, "bold"),
                 bg="#f0f4f8", fg="#2a4365").pack(pady=20)

        # Video display frame
        self.video_frame = tk.Label(self, bg="#d7e1f1", bd=2, relief='sunken')
        self.video_frame.pack(padx=40, pady=20)

        # Name input
        entry_frame = tk.Frame(self, bg="#f0f4f8")
        entry_frame.pack(pady=15)
        tk.Label(entry_frame, text="Full Name:", font=("Segoe UI", 14),
                 bg="#f0f4f8", fg="#2a4365").grid(row=0, column=0, padx=10, pady=5)
        self.name_entry = tk.Entry(entry_frame, font=("Segoe UI", 14), width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f0f4f8")
        btn_frame.pack(pady=15)
        self.btn_save = tk.Button(btn_frame, text="Capture & Enroll", command=self.start_enrollment_process)
        self.btn_save.grid(row=0, column=0, padx=15)
        self.btn_close = tk.Button(btn_frame, text="Close", command=self.close_window)
        self.btn_close.grid(row=0, column=1, padx=15)

        style_buttons(self)

        # Camera Setup
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.captured_frame = None
        self.countdown = 3  # Countdown in seconds
        self.countdown_running = False
        self.update_video()

    def draw_eye_guides(self, frame):
        """Detect both eyes and draw separate circles on each."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)
        for (ex, ey, ew, eh) in eyes[:2]:  # Draw for up to 2 eyes
            center = (ex + ew // 2, ey + eh // 2)
            radius = max(ew, eh) // 3
            cv2.circle(frame, center, radius, (0, 255, 0), 2)  # Green circle
        return frame

    def update_video(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        if ret:
            # Add eye guides
            frame = self.draw_eye_guides(frame)

            # Show countdown text if active
            if self.countdown_running:
                text = f"Capturing in {self.countdown}..."
                cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1.2, (0, 0, 255), 3, cv2.LINE_AA)

            # Store frame for later capture
            self.captured_frame = frame.copy()

            # Convert to Tkinter display
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image).resize((640, 480))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)

        self.after(30, self.update_video)

    def start_enrollment_process(self):
        """Start countdown before capturing image."""
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
        if self.countdown > 0:
            self.countdown -= 1
            self.after(1000, self._do_countdown)
        else:
            self.countdown_running = False
            success, message = self.backend.add_user(self.name_entry.get().strip(), self.captured_frame)
            if success:
                messagebox.showinfo("Success", message)
                self.close_window()
            else:
                messagebox.showerror("Error", message)

    def close_window(self):
        """Stop camera and close window."""
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

# ====================================================================
# MARK ATTENDANCE WINDOW
# ====================================================================
class MarkAttendanceApp(tk.Toplevel):
    def __init__(self, master, backend_system):
        super().__init__(master)
        self.backend = backend_system
        self.title("Smart Attendance - Mark Attendance")
        self.configure(bg="#f0f4f8")
        self.state('zoomed')

        tk.Label(self, text="Mark Attendance", font=("Segoe UI", 20, "bold"),
                 bg="#f0f4f8", fg="#2a4365").pack(pady=20)

        self.video_frame = tk.Label(self, bg="#d7e1f1", bd=2, relief='sunken')
        self.video_frame.pack(padx=40, pady=20)

        self.status_label = tk.Label(self, text="Status: Initializing...", font=("Segoe UI", 15, "italic"),
                                     bg="#f0f4f8", fg="#495f88")
        self.status_label.pack(pady=15)

        self.btn_close = tk.Button(self, text="Close", command=self.close_window)
        self.btn_close.pack(pady=10)
        style_buttons(self)

        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.update_video()

    def draw_eye_guides(self, frame):
        """Draw circles around both eyes for guidance."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)
        for (ex, ey, ew, eh) in eyes[:2]:
            center = (ex + ew // 2, ey + eh // 2)
            radius = max(ew, eh) // 3
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
        return frame

    def update_video(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        if ret:
            status_msg, status_color_bgr = self.backend.run_attendance_check(frame)
            # Add eye guides
            frame = self.draw_eye_guides(frame)
            # Status on frame
            cv2.putText(frame, status_msg, (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, status_color_bgr, 3, cv2.LINE_AA)
            self.status_label.config(text=f"Status: {status_msg}", fg="#2a4365")

            # Display in Tkinter
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image).resize((640, 480))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)

        self.after(30, self.update_video)

    def close_window(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

# ====================================================================
# HOME PAGE
# ====================================================================
class HomePage(tk.Tk):
    def __init__(self, backend_system):
        super().__init__()
        self.backend_system = backend_system
        self.title("Smart Attendance System")
        self.configure(bg="#1f2937")
        self.state('zoomed')

        # Fonts
        self.font_bold = tkFont.Font(family="Helvetica", size=28, weight="bold")
        self.font_regular = tkFont.Font(family="Helvetica", size=14)
        self.font_button = tkFont.Font(family="Helvetica", size=16, weight="bold")

        # Title
        tk.Label(self, text="Smart Attendance System", font=self.font_bold,
                 bg="#1f2937", fg="#0ee9d2").pack(pady=50)
        tk.Label(self, text="Welcome! Please choose an option below.",
                 font=self.font_regular, bg="#1f2937", fg="#5eead4").pack(pady=10)

        # Card layout
        card_frame = tk.Frame(self, bg="#bcd2f0")
        card_frame.pack(pady=60, expand=True, fill="both")
        card_style = {"bg": "#111827", "relief": "raised", "bd": 0,
                      "highlightthickness": 2, "highlightbackground": "#0ee9d2",
                      "cursor": "hand2"}

        # Enrollment card
        enroll_card = tk.Frame(card_frame, **card_style)
        enroll_card.pack(side="left", padx=80, pady=20, expand=True, fill="both")
        tk.Label(enroll_card, text="🧑💼", font=("Helvetica", 70), bg="#111827", fg="#0ee9d2").pack(pady=(50, 12))
        tk.Label(enroll_card, text="Enroll User", font=self.font_bold, bg="#111827", fg="#0ee9d2").pack(pady=8)
        tk.Button(enroll_card, text="Launch Enrollment", font=self.font_button, bg="#10b981", fg="white",
                  activebackground="#0f766e", activeforeground="white", bd=0, padx=30, pady=16,
                  command=self.open_enrollment).pack(pady=50)

        # Attendance card
        attendance_card = tk.Frame(card_frame, **card_style)
        attendance_card.pack(side="right", padx=80, pady=20, expand=True, fill="both")
        tk.Label(attendance_card, text="✅", font=("Helvetica", 70), bg="#111827", fg="#0ee9d2").pack(pady=(50, 12))
        tk.Label(attendance_card, text="Mark Attendance", font=self.font_bold, bg="#111827", fg="#0ee9d2").pack(pady=8)
        tk.Button(attendance_card, text="Launch Attendance", font=self.font_button, bg="#10b981", fg="white",
                  activebackground="#0f766e", activeforeground="white", bd=0, padx=30, pady=16,
                  command=self.open_mark_attendance).pack(pady=50)

        style_buttons(self)

    def open_enrollment(self):
        EnrollmentApp(self, self.backend_system)

    def open_mark_attendance(self):
        MarkAttendanceApp(self, self.backend_system)

# ====================================================================
# MAIN ENTRY
# ====================================================================
if __name__ == "__main__":
    system_backend = backend.AttendanceSystem()
    app = HomePage(backend_system=system_backend)
    app.mainloop()

