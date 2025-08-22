import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import sqlite3
import io
import time

# ======== SETTINGS & COLOR PALETTE ========
PRIMARY = "#226B6F"     # deep teal
DARKER = "#16383b"      # very dark teal/navy
ACCENT = "#18bc9c"      # turquoise
BG = "#f3f6f7"          # near-white cool gray
SIDEBAR_BG = "#184B4C"  # sidebar slightly darker
WHITE = "#FFFFFF"

FONT_MAIN = ("Segoe UI", 13)
FONT_HEADER = ("Segoe UI", 22, "bold")
FONT_CARD = ("Segoe UI", 16, "bold")

DB_NAME = "user_enrollment.db"
TABLE_NAME = "users"
CIRCLE_DIAMETER = 300

FEEDBACK_STATES = [
    ("Please Blink", (255, 215, 0)), # Gold
    ("Verified!", (0, 255, 0)), # Green
    ("Unknown User", (255, 0, 0)), # Red
]
FEEDBACK_KEYS = {"b": 0, "v": 1, "u": 2}

# ========== DATABASE ==========
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
        self.update_video()

    def update_video(self):
        if not self.running: return
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
        # Optional: Save face embedding here.
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
        style.configure("TButton", font=FONT_CARD, padding=(10, 10))

        ttk.Label(self, text="✅ Smart Attendance System", style="Header.TLabel").pack(pady=18)
        ttk.Label(self, text="👋 Please look into the camera and wait for recognition.").pack(pady=8)

        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=14)
        ttk.Label(entry_frame, text="📝 Full Name:", font=FONT_CARD).grid(row=0, column=0, padx=8)
        self.name_entry = ttk.Entry(entry_frame, font=FONT_MAIN, width=28)
        self.name_entry.grid(row=0, column=1, padx=8)

        self.video_border = tk.Frame(self, bg="#dbeeee", bd=2, relief="ridge")
        self.video_border.pack(pady=22)
        self.video_frame = tk.Label(self.video_border, bg="#dbeeee", width=500, height=360)
        self.video_frame.pack()

        self.feedback_label = ttk.Label(self, text="Status: Waiting for recognition...", font=("Segoe UI", 13, "italic"))
        self.feedback_label.pack(pady=8)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=26)
        self.btn_save = ttk.Button(btn_frame, text="💾 Save Photo", command=self.save_photo)
        self.btn_save.grid(row=0, column=0, padx=18)
        self.btn_quit = ttk.Button(btn_frame, text="❌ Close", command=self.quit_app)
        self.btn_quit.grid(row=0, column=1, padx=18)

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

        # Draw circular overlay
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

# ========== MODERN MAIN HOME PAGE ==========
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
            ("📊", "Report", self.open_reports),
            ("⚙", "Settings", self.open_settings)
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

        # Footer
        footer = tk.Frame(self, bg=SIDEBAR_BG, height=32)
        footer.pack(fill="x", side="bottom")
        lbl_footer = tk.Label(
            footer, text="© 2025 Smart Attendance System. All Rights Reserved.",
            font=("Segoe UI", 9, "italic"), fg="white", bg=SIDEBAR_BG
        )
        lbl_footer.pack(pady=6)

    def update_clock(self):
        now = time.strftime("%A %I:%M %p")
        self.clock_lbl.config(text=now)
        self.after(1000, self.update_clock)

    def open_enrollment(self):
        EnrollmentApp(self)

    def open_mark_attendance(self):
        MarkAttendanceApp(self)

    def open_reports(self):
        messagebox.showinfo("Reports", "Report functionality coming soon.")

    def open_settings(self):
        messagebox.showinfo("Settings", "Settings functionality coming soon.")

# ======= MAIN ENTRY POINT ==========
if __name__ == "__main__":
    setup_database()
    app = HomePage()
    app.mainloop()

