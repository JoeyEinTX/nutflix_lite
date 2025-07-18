#!/usr/bin/env python3
"""
Nutflix Lite – Local-Only Camera Debugging GUI (With nutflix_common motion utils)
Dual camera preview + motion logs using reusable motion detection
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
from nutflix_common.motion_utils import MotionDetector, MotionConfig
from nutflix_common.logger import get_logger, configure_from_config
from camera_manager import CameraManager

class NutflixLiteGUI:
    def __init__(self, root, config_path="config.yaml"):
        self.root = root
        
        # Initialize logger first
        self.logger = get_logger("gui")
        
        # Load configuration
        try:
            self.config = load_config(config_path)
            self.log_message(f"Configuration loaded from: {config_path}")
            
            # Configure logging from config
            configure_from_config(self.config)
            self.logger.info("Logging configured from config file")
            
        except Exception as e:
            # Fallback to default config if loading fails
            self.config = self._get_default_config()
            self.log_message(f"Using default config due to error: {e}")
            self.logger.warning(f"Config loading failed, using defaults: {e}")
        
        # Extract configuration values
        self.app_config = self.config.get('app_name', 'Nutflix Lite')
        self.gui_config = self.config.get('gui', {})
        self.motion_config_dict = self.config.get('motion_detection', {})
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
        self.log(f"{self.app_config} started with motion utilities!")
        
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
            self.logger.info(f"Camera manager initialized in {camera_info['critter_cam']['type']} mode")
        except Exception as e:
            self.log(f"❌ Camera initialization failed: {e}")
            self.logger.error(f"Camera initialization failed: {e}")
            self.camera_manager = None

        # Initialize Motion Detector with config
        motion_config = MotionConfig(
            threshold=self.motion_config_dict.get('threshold', 500),
            sensitivity=self.motion_config_dict.get('sensitivity', 25),
            cooldown=self.motion_config_dict.get('cooldown', 2.0)
        )
        self.motion_detector = MotionDetector(motion_config)
        self.log(f"Motion detector initialized: threshold={motion_config.threshold}, cooldown={motion_config.cooldown}s")
        self.logger.info(f"Motion detector configured: threshold={motion_config.threshold}, cooldown={motion_config.cooldown}s")

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
            motion_detected = self.motion_detector.process_frame(critter_frame, "critter_cam")
            if motion_detected:
                self.log_motion_event("CritterCam")
            self.display_frame(critter_frame, self.critter_canvas)

        # Process NutCam  
        if nut_frame is not None:
            motion_detected = self.motion_detector.process_frame(nut_frame, "nut_cam")
            if motion_detected:
                self.log_motion_event("NutCam")
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

    def log_motion_event(self, camera_name):
        """Log a motion detection event with additional stats."""
        camera_id = "critter_cam" if camera_name == "CritterCam" else "nut_cam"
        stats = self.motion_detector.get_camera_stats(camera_id)
        
        self.log(f"🔴 MOTION DETECTED in {camera_name}! "
                f"(Events: {stats['motion_events_count']}, "
                f"Frames: {stats['frames_processed']})")
        
        # Also log to structured logger
        self.logger.info(f"Motion detected in {camera_name} - Events: {stats['motion_events_count']}, Frames: {stats['frames_processed']}")

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)

    def shutdown(self):
        self.running = False
        if self.camera_manager:
            self.camera_manager.release()
        
        # Log final motion detection stats
        for camera_id in ["critter_cam", "nut_cam"]:
            stats = self.motion_detector.get_camera_stats(camera_id)
            if stats['frames_processed'] > 0:
                self.log(f"Final stats for {camera_id}: "
                        f"{stats['frames_processed']} frames, "
                        f"{stats['motion_events_count']} motion events")
        
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = NutflixLiteGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.shutdown)
    root.mainloop()
