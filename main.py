#!/usr/bin/env python3
"""
Nutflix Lite – Local-Only Camera Debugging GUI
Dual camera preview + motion logs
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import cv2
import numpy as np
from PIL import Image, ImageTk

# CAMERA IDs (customize if needed)
CRITTER_CAM_ID = 0
NUT_CAM_ID = 1

# Motion detection parameters
MOTION_THRESHOLD = 500  # Minimum contour area to consider as motion
MOTION_SENSITIVITY = 25  # Threshold for frame difference

class NutflixLiteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nutflix Lite (Local)")
        self.root.geometry("1280x720")
        self.root.configure(bg="#111")

        # Frames
        self.critter_label = tk.Label(root, text="CritterCam", fg="white", bg="#111")
        self.critter_label.pack()
        self.critter_canvas = tk.Label(root)
        self.critter_canvas.pack()

        self.nut_label = tk.Label(root, text="NutCam", fg="white", bg="#111")
        self.nut_label.pack()
        self.nut_canvas = tk.Label(root)
        self.nut_canvas.pack()

        # Log window
        self.log_area = scrolledtext.ScrolledText(root, height=8, bg="#222", fg="#0f0", font=("Courier", 10))
        self.log_area.pack(fill="x")
        self.log("Nutflix Lite started.")

        # Video capture threads
        self.critter_cam = cv2.VideoCapture(CRITTER_CAM_ID)
        self.nut_cam = cv2.VideoCapture(NUT_CAM_ID)

        # Motion detection variables
        self.critter_bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        self.nut_bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        
        # Previous frames for motion detection
        self.critter_prev_frame = None
        self.nut_prev_frame = None
        
        # Motion detection cooldown (prevent spam logging)
        self.critter_last_motion = 0
        self.nut_last_motion = 0
        self.motion_cooldown = 2.0  # seconds between motion logs

        self.running = True
        self.update_video()

    def update_video(self):
        # Show CritterCam
        if self.critter_cam.isOpened():
            ret, frame = self.critter_cam.read()
            if ret:
                self.detect_motion(frame, "CritterCam", self.critter_bg_subtractor, 
                                 self.critter_last_motion, "critter")
                self.display_frame(frame, self.critter_canvas)

        # Show NutCam
        if self.nut_cam.isOpened():
            ret, frame = self.nut_cam.read()
            if ret:
                self.detect_motion(frame, "NutCam", self.nut_bg_subtractor,
                                 self.nut_last_motion, "nut")
                self.display_frame(frame, self.nut_canvas)

        if self.running:
            self.root.after(30, self.update_video)

    def display_frame(self, frame, canvas):
        resized = cv2.resize(frame, (640, 360))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.imgtk = imgtk
        canvas.configure(image=imgtk)

    def detect_motion(self, frame, camera_name, bg_subtractor, last_motion_time, camera_type):
        """Detect motion in the given frame and log if motion is found"""
        current_time = time.time()
        
        # Skip if we're in cooldown period
        if camera_type == "critter":
            if current_time - self.critter_last_motion < self.motion_cooldown:
                return
        else:
            if current_time - self.nut_last_motion < self.motion_cooldown:
                return
        
        # Convert to grayscale for motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Apply background subtraction
        fg_mask = bg_subtractor.apply(gray)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check if any significant motion is detected
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > MOTION_THRESHOLD:
                motion_detected = True
                break
        
        # Log motion if detected
        if motion_detected:
            self.log(f"🔴 MOTION DETECTED in {camera_name}!")
            if camera_type == "critter":
                self.critter_last_motion = current_time
            else:
                self.nut_last_motion = current_time

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)

    def shutdown(self):
        self.running = False
        self.critter_cam.release()
        self.nut_cam.release()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = NutflixLiteGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.shutdown)
    root.mainloop()
