"""
File name      : multi_enroll_gui.py
Description    : A graphical user interface for enrolling new users into the
                 Smart Attendance System.
Author         : Ragini
Contributor    : Chaitanya (Backend Integration)
"""

# ==============================================================================
# SECTION 1: IMPORTS
# ==============================================================================
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import face_recognition
import database as db

# ==============================================================================
# SECTION 2: GUI APPLICATION CLASS
# ==============================================================================
class EnrollmentApp:
    def __init__(self, master):
        """
        Function name  : __init__
        Description    : Initializes the main application window and its widgets.
        Author         : Ragini
        """
        self.master = master
        self.master.title("Smart Attendance - User Enrollment")
        self.master.configure(bg="#f7f9fc")
        self.master.geometry("700x650")
        self.master.resizable(False, False)

        # --- Style (modern ttk) ---
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), background="#f7f9fc", foreground="#37474F")
        style.configure("Header.TLabel", font=("Helvetica", 20, "bold"), foreground="#2c3e50")
        style.configure("TButton", font=("Helvetica", 13), padding=6)
        style.map("TButton",
                  background=[("active", "#1976D2")],
                  foreground=[("active", "white")])

        # --- All widget definitions (Title, Entry, Video Frame, Buttons) ---
        self.title_label = ttk.Label(master, text="Smart Attendance System", style="Header.TLabel")
        self.title_label.pack(pady=12)
        self.subtitle = ttk.Label(master, text="Please look into the camera and enter your name below.")
        self.subtitle.pack(pady=4)
        self.entry_frame = ttk.Frame(master)
        self.entry_frame.pack(pady=10)
        ttk.Label(self.entry_frame, text="Full Name:", font=("Helvetica", 13)).grid(row=0, column=0, padx=5)
        self.name_entry = ttk.Entry(self.entry_frame, font=("Helvetica", 13), width=28)
        self.name_entry.grid(row=0, column=1, padx=5)
        self.video_border = tk.Frame(master, bg="#dfe6e9", bd=2, relief="ridge")
        self.video_border.pack(pady=15)
        self.video_frame = tk.Label(self.video_border, bg="#dfe6e9", width=500, height=360)
        self.video_frame.pack()
        self.feedback_label = ttk.Label(master, text="Status: Waiting for input...", font=("Helvetica", 12, "italic"))
        self.feedback_label.pack(pady=6)
        btn_frame = ttk.Frame(master)
        btn_frame.pack(pady=15)
        self.btn_save = ttk.Button(btn_frame, text="Save Photo & Enroll", command=self.save_photo)
        self.btn_save.grid(row=0, column=0, padx=15)
        self.btn_quit = ttk.Button(btn_frame, text="Quit", command=self.quit_app)
        self.btn_quit.grid(row=0, column=1, padx=15)

        # --- Camera Setup ---
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not access the camera.")
            self.master.destroy()
            return
        self.saved_frame = None
        self.update_video()

    def update_video(self):
        """
        Function name  : update_video
        Description    : Continuously captures frames from the camera and displays
                         them in the Tkinter window.
        Author         : Ragini
        """
        ret, frame = self.cap.read()
        if not ret:
            # ... (video update logic)
            return

        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image).resize((500, 360)))
        self.video_frame.imgtk = imgtk
        self.video_frame.config(image=imgtk)
        self.saved_frame = frame.copy()
        self.master.after(20, self.update_video)

    def save_photo(self):
        """
        Function name  : save_photo
        Description    : When the save button is clicked, this function captures the
                         current frame, generates a face embedding, and saves the
                         new user profile to the central database.
        Author         : Ragini
        Modified by    : Chaitanya (for backend integration)
        """
        username = self.name_entry.get().strip()
        if not username:
            messagebox.showwarning("Input Required", "Please enter a name before saving.")
            return

        if self.saved_frame is None:
            messagebox.showerror("Error", "No frame captured from camera.")
            return

        # ----------------------------------------------------------------------
        """
        # INTEGRATION CHANGE: Replaced old database logic with new embedding logic.
        # Author: Chaitanya
        """
        # ----------------------------------------------------------------------
        # 1. Find the face in the saved frame.
        face_locations = face_recognition.face_locations(self.saved_frame)

        # 2. Check if exactly one face is found.
        if len(face_locations) == 1:
            # 3. Generate the embedding for the face.
            embedding = face_recognition.face_encodings(self.saved_frame, face_locations)[0]
            embedding_list = embedding.tolist()

            # 4. Save to our central database using the imported function.
            db.add_user(username, embedding_list)
            messagebox.showinfo("Success", f"User '{username}' has been enrolled successfully!")
            
        elif len(face_locations) > 1:
            messagebox.showerror("Error", "Multiple faces detected. Please ensure only one person is in the frame.")
        else:
            messagebox.showerror("Error", "No face was detected. Please try again.")

    def quit_app(self):
        """
        Function name  : quit_app
        Description    : Releases the camera and closes the application.
        Author         : Ragini
        """
        if self.cap.isOpened():
            self.cap.release()
        self.master.destroy()

# ==============================================================================
# SECTION 3: MAIN EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    # Task: Initialize the Tkinter root window and start the application.
    root = tk.Tk()
    app = EnrollmentApp(root)
    root.mainloop()