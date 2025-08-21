import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import cv2
import sqlite3
import io
import threading

DB_NAME = "user_enrollment.db"
TABLE_NAME = "users"
CIRCLE_DIAMETER = 300  # diameter of circular overlay

FEEDBACK_STATES = [
    ("Please Blink", (255, 215, 0)),  # Gold
    ("Verified!", (0, 255, 0)),       # Green
    ("Unknown User", (255, 0, 0)),    # Red
]

FEEDBACK_KEYS = {"b": 0, "v": 1, "u": 2}

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_to_database(username, image_bytes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f"INSERT INTO {TABLE_NAME} (name, image) VALUES (?, ?)", (username, image_bytes))
    conn.commit()
    conn.close()
    print(f"Saved image for user: {username}")

class EnrollmentApp(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Smart Attendance System - Enrollment")
        self.configure(bg='#ECEFF1')
        self.cap = cv2.VideoCapture(0)

        tk.Label(self, text="Enter Name:", font=('Helvetica', 12), bg='#ECEFF1').pack(pady=5)
        self.name_entry = tk.Entry(self, font=('Helvetica', 12))
        self.name_entry.pack(pady=5)

        self.video_frame = tk.Label(self, bg='#B0BEC5')
        self.video_frame.pack(padx=20, pady=10)

        self.btn_save = tk.Button(self, text="Save User", command=self.save_user, bg='#03A9F4', fg='white')
        self.btn_save.pack(pady=5)

        self.btn_close = tk.Button(self, text="Close", command=self.close, bg='#607D8B', fg='white')
        self.btn_close.pack(pady=5)

        self.running = True
        self.update_video()

    def update_video(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im_pil = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=im_pil.resize((450, 340)))
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
            self.frame = frame
        self.after(15, self.update_video)

    def save_user(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name!")
            return
        # Add your face embedding saving logic if needed here
        messagebox.showinfo("Success", f"User {name} enrolled successfully!")

    def close(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

class MarkAttendanceApp(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("🎥 Smart Attendance - Mark Attendance")
        self.configure(bg="#f7f9fc")
        self.geometry("700x650")
        self.resizable(False, False)

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TLabel", font=("Helvetica", 12), background="#f7f9fc", foreground="#37474F")
        style.configure("Header.TLabel", font=("Helvetica", 20, "bold"), foreground="#2c3e50")
        style.configure("TButton", font=("Helvetica", 13), padding=6)
        style.map("TButton",
                  background=[("active", "#1976D2")],
                  foreground=[("active", "white")])

        ttk.Label(self, text="Smart Attendance System", style="Header.TLabel").pack(pady=12)
        ttk.Label(self, text="👋 Please look into the camera and wait for recognition.").pack(pady=4)

        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=10)
        ttk.Label(entry_frame, text="Full Name:", font=("Helvetica", 13)).grid(row=0, column=0, padx=5)
        self.name_entry = ttk.Entry(entry_frame, font=("Helvetica", 13), width=28)
        self.name_entry.grid(row=0, column=1, padx=5)

        self.video_border = tk.Frame(self, bg="#dfe6e9", bd=2, relief="ridge")
        self.video_border.pack(pady=15)
        self.video_frame = tk.Label(self.video_border, bg="#dfe6e9", width=500, height=360)
        self.video_frame.pack()

        self.feedback_label = ttk.Label(self, text="Status: Waiting for recognition...", font=("Helvetica", 12, "italic"))
        self.feedback_label.pack(pady=6)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)
        self.btn_save = ttk.Button(btn_frame, text="💾 Save Photo", command=self.save_photo)
        self.btn_save.grid(row=0, column=0, padx=15)
        self.btn_quit = ttk.Button(btn_frame, text="❌ Close", command=self.quit_app)
        self.btn_quit.grid(row=0, column=1, padx=15)

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "⚠️ Could not access the camera.")
            self.destroy()
            return

        self.saved_frame = None
        self.feedback_state = 0
        self.update_video()

    def update_video(self):
        ret, frame = self.cap.read()
        if not ret:
            self.video_frame.config(text="Camera not found")
            self.after(20, self.update_video)
            return

        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        r = CIRCLE_DIAMETER // 2

        # Draw circular overlay instead of rectangle
        frame_overlay = frame.copy()
        cv2.circle(frame_overlay, (cx, cy), r, (0, 120, 255), thickness=3)

        msg, color_bgr = FEEDBACK_STATES[self.feedback_state]
        cv2.putText(frame_overlay, msg, (60, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, color_bgr, 3, cv2.LINE_AA)
        self.feedback_label.config(text=f"Status: {msg}")

        cv2image = cv2.cvtColor(frame_overlay, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image).resize((500, 360)))
        self.video_frame.imgtk = imgtk
        self.video_frame.config(image=imgtk)

        self.saved_frame = frame.copy()
        self.after(20, self.update_video)

    def save_photo(self):
        username = self.name_entry.get().strip()
        if not username:
            messagebox.showwarning("Input Required", "⚠️ Please enter a name before saving.")
            return

        im_pil = Image.fromarray(cv2.cvtColor(self.saved_frame, cv2.COLOR_BGR2RGB))
        with io.BytesIO() as output:
            im_pil.save(output, format="JPEG")
            img_bytes = output.getvalue()
        save_to_database(username, img_bytes)
        messagebox.showinfo("Saved", f"✅ Photo for {username} saved successfully!")

    def quit_app(self):
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

class HomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Attendance System")
        self.geometry("580x350")
        self.configure(bg="#e7f4f2")
        self.resizable(False, False)

        header = tk.Frame(self, bg="#209e71", height=60)
        header.pack(fill="x", side="top")

        lbl_header = tk.Label(header, text="Smart Attendance System", font=("Segoe UI", 22, "bold"),
                              fg="white", bg="#209e71")
        lbl_header.pack(pady=8)

        btn_frame = tk.Frame(self, bg="#e7f4f2")
        btn_frame.pack(pady=60)

        btn_enroll = tk.Button(btn_frame, text="Enroll User", command=self.open_enrollment,
                               width=18, height=2, bg="#209e71", fg="white", font=("Segoe UI", 16, "bold"),
                               relief="raised", cursor="hand2")
        btn_enroll.grid(row=0, column=0, padx=25)

        btn_mark_attendance = tk.Button(btn_frame, text="Mark Attendance", command=self.open_mark_attendance,
                                        width=18, height=2, bg="#388e3c", fg="white", font=("Segoe UI", 16, "bold"),
                                        relief="raised", cursor="hand2")
        btn_mark_attendance.grid(row=0, column=1, padx=25)

        footer = tk.Frame(self, bg="#209e71", height=30)
        footer.pack(fill="x", side="bottom")

        lbl_footer = tk.Label(footer, text="© 2025 Smart Attendance System. All Rights Reserved.",
                              font=("Segoe UI", 9, "italic"), fg="white", bg="#209e71")
        lbl_footer.pack(pady=5)

    def open_enrollment(self):
        EnrollmentApp(self)

    def open_mark_attendance(self):
        MarkAttendanceApp(self)

if __name__ == "__main__":
    setup_database()
    app = HomePage()
    app.mainloop()
