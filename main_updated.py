#!/usr/bin/env python3
"""
Nutflix Lite – Local-Only Camera Debugging GUI (Updated with nutflix_common)
Dual camera preview + motion logs + config system
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import cv2
import numpy as np
from PIL import Image, ImageTk

# Import from our nutflix_common package
from nutflix_common.config_loader import load_config
from camera_manager import CameraManager

class NutflixLiteGUI:
    def __init__(self, root, config_path="config.yaml"):
        self.root = root
        
        # Load configuration
        try:
            self.config = load_config(config_path)
            self.log_message(f"Configuration loaded from: {config_path}")
        except Exception as e:
            # Fallback to default config if loading fails
            self.config = self._get_default_config()
            self.log_message(f"Using default config due to error: {e}")
        
        # Extract configuration values
        self.app_config = self.config.get('app_name', 'Nutflix Lite')
        self.gui_config = self.config.get('gui', {})
        self.motion_config = self.config.get('motion_detection', {})
        self.camera_config = self.config.get('cameras', {})
        
        # Set up GUI
        self.root.title(f"{self.app_config} (Local)")
        self.root.geometry(f"{self.gui_config.get('window_width', 1280)}x{self.gui_config.get('window_height', 720)}")
        self.root.configure(bg=self.gui_config.get('background_color', '#111'))

        # Camera labels and canvases
        self.critter_label = tk.Label(root, text="CritterCam", fg="white", bg=self.gui_config.get('background_color', '#111'))
        self.critter_label.pack()
        self.critter_canvas = tk.Label(root)
        self.critter_canvas.pack()

        self.nut_label = tk.Label(root, text="NutCam", fg="white", bg=self.gui_config.get('background_color', '#111'))
        self.nut_label.pack()
        self.nut_canvas = tk.Label(root)
        self.nut_canvas.pack()

        # Log window
        self.log_area = scrolledtext.ScrolledText(
            root, 
            height=self.gui_config.get('log_height', 8), 
            bg=self.gui_config.get('log_bg_color', '#222'), 
            fg=self.gui_config.get('log_fg_color', '#0f0'), 
            font=("Courier", 10)
        )
        self.log_area.pack(fill="x")
        
        # Initialize message buffer for early logging
        self._early_messages = []
        
        # Log startup message
        self.log(f"{self.app_config} started with config-driven setup!")
        
        # Flush early messages
        for msg in self._early_messages:
            self.log_area.insert(tk.END, msg + "\n")
        self._early_messages.clear()

        # Initialize Camera Manager with config
        try:
            self.camera_manager = CameraManager(self.camera_config)
            camera_info = self.camera_manager.get_camera_info()
            self.log(f"Camera system: {camera_info['critter_cam']['type']} mode")
            self.log(f"CritterCam: {'✓' if camera_info['critter_cam']['available'] else '✗'}")
            self.log(f"NutCam: {'✓' if camera_info['nut_cam']['available'] else '✗'}")
        except Exception as e:
            self.log(f"❌ Camera initialization failed: {e}")
            self.camera_manager = None

        # Motion detection variables
        self.critter_bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        self.nut_bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        
        # Motion detection settings from config
        self.motion_threshold = self.motion_config.get('threshold', 500)
        self.motion_sensitivity = self.motion_config.get('sensitivity', 25)
        self.motion_cooldown = self.motion_config.get('cooldown', 2.0)
        
        # Motion detection cooldown tracking
        self.critter_last_motion = 0
        self.nut_last_motion = 0

        self.running = True
        self.update_video()

    def _get_default_config(self):
        """Fallback configuration if config file loading fails."""
        return {
            'app_name': 'Nutflix Lite',
            'cameras': {
                'critter_cam_id': 0,
                'nut_cam_id': 1,
                'debug_mode': True
            },
            'motion_detection': {
                'threshold': 500,
                'sensitivity': 25,
                'cooldown': 2.0
            },
            'gui': {
                'window_width': 1280,
                'window_height': 720,
                'background_color': '#111',
                'log_height': 8,
                'log_bg_color': '#222',
                'log_fg_color': '#0f0'
            }
        }

    def log_message(self, message):
        """Helper for early logging before GUI is ready."""
        if hasattr(self, 'log_area'):
            self.log(message)
        else:
            self._early_messages.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def update_video(self):
        if not self.camera_manager:
            # Skip video update if camera manager failed to initialize
            if self.running:
                self.root.after(100, self.update_video)
            return

        # Get frames from both cameras
        frames = self.camera_manager.read_frames()
        critter_frame = frames['critter_cam']
        nut_frame = frames['nut_cam']

        # Process CritterCam
        if critter_frame is not None:
            self.detect_motion(critter_frame, "CritterCam", self.critter_bg_subtractor, "critter")
            self.display_frame(critter_frame, self.critter_canvas)

        # Process NutCam  
        if nut_frame is not None:
            self.detect_motion(nut_frame, "NutCam", self.nut_bg_subtractor, "nut")
            self.display_frame(nut_frame, self.nut_canvas)

        if self.running:
            self.root.after(30, self.update_video)

    def display_frame(self, frame, canvas):
        resized = cv2.resize(frame, (640, 360))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.imgtk = imgtk
        canvas.configure(image=imgtk)

    def detect_motion(self, frame, camera_name, bg_subtractor, camera_type):
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
            if cv2.contourArea(contour) > self.motion_threshold:
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
        if self.camera_manager:
            self.camera_manager.release()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = NutflixLiteGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.shutdown)
    root.mainloop()
