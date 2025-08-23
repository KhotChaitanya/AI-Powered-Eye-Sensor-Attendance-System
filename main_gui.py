import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import io
import time
import numpy as np

# === Import backend system ===
from backend import AttendanceSystem
from iris_engine import create_iris_code

# ======== SETTINGS & COLOR PALETTE ========
PRIMARY = "#226B6F"
DARKER = "#16383b"
ACCENT = "#18bc9c"
BG = "#f3f6f7"
SIDEBAR_BG = "#184B4C"
WHITE = "#FFFFFF"

FONT_MAIN = ("Segoe UI", 13)
FONT_HEADER = ("Segoe UI", 22, "bold")
FONT_CARD = ("Segoe UI", 16, "bold")

CIRCLE_DIAMETER = 300

FEEDBACK_STATES = [
    ("Please Blink", (255, 215, 0)), # Gold
    ("Verified!", (0, 255, 0)),      # Green
    ("Unknown User", (255, 0, 0)),   # Red
]

# === Global backend instance ===
backend = AttendanceSystem()

# ========== ENROLLMENT WINDOW ==========
class EnrollmentApp(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Smart Attendance System - Enrollment")
        self.configure(bg=BG)

        tk.Label(self, text="🧑‍💼 Enter Name:", font=FONT_MAIN, bg=BG).pack(pady=10, padx=10)
        self.name_entry = tk.Entry(self, font=FONT_MAIN)
        self.name_entry.pack(pady=8, padx=16, ipadx=7, ipady=4)

        self.video_frame = tk.Label(self, bg="#d0dedc")
        self.video_frame.pack(padx=24, pady=12)

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=12)
        self.btn_save = tk.Button(
            btn_frame, text="💾 Save User", command=self.save_user,
            bg=PRIMARY, fg='white', font=FONT_CARD, width=14, height=1,
            relief="raised", bd=2, cursor="hand2", activebackground=ACCENT
        )
        self.btn_save.grid(row=0, column=0, padx=10)
        self.btn_close = tk.Button(
            btn_frame, text="❌ Close", command=self.close,
            bg=DARKER, fg='white', font=FONT_CARD, width=14, height=1,
            relief="raised", bd=2, cursor="hand2", activebackground="#455A64"
        )
        self.btn_close.grid(row=0, column=1, padx=10)

        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.frame = None
        self.update_video()

    def update_video(self):
        if not self.running: return
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame.copy()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im_pil = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=im_pil.resize((450, 340)))
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
        self.after(15, self.update_video)

    def save_user(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name!")
            return
        if self.frame is None:
            messagebox.showerror("Error", "No frame captured!")
            return

        # Dummy face embedding (replace with real embedding extractor if available)
        embedding = np.random.rand(128).tolist()

        # TODO: crop eye region from self.frame instead of using placeholder
        iris_template = create_iris_code("sample_eye.jpg")

        backend.add_user(name, embedding, iris_template.code.tolist())
        messagebox.showinfo("Success", f"User {name} enrolled successfully!")

    def close(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

# ========== MARK ATTENDANCE WINDOW ==========
class MarkAttendanceApp(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Smart Attendance - Mark Attendance")
        self.configure(bg=BG)
        self.geometry("720x680")
        self.resizable(False, False)

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TLabel", font=FONT_MAIN, background=BG, foreground=DARKER)
        style.configure("Header.TLabel", font=FONT_HEADER, foreground=PRIMARY)

        ttk.Label(self, text="✅ Smart Attendance System", style="Header.TLabel").pack(pady=18)
        self.video_border = tk.Frame(self, bg="#dbeeee", bd=2, relief="ridge")
        self.video_border.pack(pady=22)
        self.video_frame = tk.Label(self.video_border, bg="#dbeeee", width=500, height=360)
        self.video_frame.pack()

        self.feedback_label = ttk.Label(self, text="Status: Waiting...", font=("Segoe UI", 13, "italic"))
        self.feedback_label.pack(pady=8)

        self.cap = cv2.VideoCapture(0)
        self.update_video()

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            status, color = backend.run_attendance_check(frame)
            cv2.putText(frame, status, (60, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            self.feedback_label.config(text=f"Status: {status}")

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image).resize((500, 360)))
            self.video_frame.imgtk = imgtk
            self.video_frame.config(image=imgtk)
        self.after(30, self.update_video)

    def quit_app(self):
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

# ========== HOME PAGE ==========
class HomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Attendance System")
        self.geometry("860x480")
        self.configure(bg=BG)
        self.resizable(False, False)

        # Sidebar
        sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=95)
        sidebar.pack(side="left", fill="y")

        for i, (icon, text, cmd) in enumerate([
            ("🏠", "Home", None),
            ("🧑‍💼", "Enroll", self.open_enrollment),
            ("✅", "Mark", self.open_mark_attendance),
        ]):
            btn = tk.Button(sidebar, text=f"{icon}\n{text}", font=FONT_MAIN, bg=SIDEBAR_BG, fg="white", bd=0,
                            relief="flat", activebackground=PRIMARY, activeforeground="white",
                            command=cmd if cmd else lambda: None, cursor="hand2")
            btn.pack(pady=10, fill="x", ipadx=2, ipady=5)

        # Header
        header = tk.Frame(self, bg=BG)
        header.pack(side="top", fill="x", pady=(18, 0), padx=(125, 35))
        tk.Label(header, text="Smart Attendance System", font=FONT_HEADER, fg=PRIMARY, bg=BG).pack(anchor='w')
        self.clock_lbl = tk.Label(header, text="", font=("Segoe UI", 11), bg=BG, fg=ACCENT)
        self.clock_lbl.pack(anchor='e')
        self.update_clock()

        # Main Cards Section
        main = tk.Frame(self, bg=BG)
        main.pack(padx=(140,32), pady=(46,20), fill="both", expand=True)

        for i, (emoji, title, desc, cmd) in enumerate([
            ("🧑‍💼", "Enroll User", "Add a new face and name to the system.", self.open_enrollment),
            ("✅", "Mark Attendance", "Recognize and mark present.", self.open_mark_attendance),
        ]):
            card = tk.Frame(main, bg=WHITE, relief="raised", bd=3)
            card.grid(row=0, column=i, padx=26, pady=8, ipadx=18, ipady=5, sticky="nsew")
            tk.Label(card, text=emoji, font=("Segoe UI", 50), bg=WHITE).pack(pady=(10,0))
            tk.Label(card, text=title, font=FONT_CARD, fg=PRIMARY, bg=WHITE).pack(pady=(4,4))
            tk.Label(card, text=desc, font=FONT_MAIN, fg="#444", bg=WHITE).pack(pady=(0,11))
            tk.Button(card, text="Launch", font=FONT_MAIN, bg=PRIMARY, fg="white", width=13,
                      command=cmd, cursor="hand2", relief="raised", activebackground=ACCENT).pack(pady=(0,13))

    def update_clock(self):
        now = time.strftime("%A %I:%M %p")
        self.clock_lbl.config(text=now)
        self.after(1000, self.update_clock)

    def open_enrollment(self):
        EnrollmentApp(self)

    def open_mark_attendance(self):
        MarkAttendanceApp(self)

# ======= MAIN ENTRY POINT ==========
if __name__ == "__main__":
    app = HomePage()
    app.mainloop()
