#!/usr/bin/env python3
"""
Integration example showing how to use CameraManager with the existing GUI
"""

# Example of how to modify your main.py to use CameraManager

# OLD CODE (in your current main.py):
# self.critter_cam = cv2.VideoCapture(CRITTER_CAM_ID)
# self.nut_cam = cv2.VideoCapture(NUT_CAM_ID)

# NEW CODE (using CameraManager):
from camera_manager import CameraManager

# In your NutflixLiteGUI.__init__ method, replace camera initialization with:
"""
# Camera configuration
camera_config = {
    'critter_cam_id': CRITTER_CAM_ID,
    'nut_cam_id': NUT_CAM_ID
}

# Initialize camera manager
self.camera_manager = CameraManager(camera_config)
self.log(f"Camera system initialized: {self.camera_manager.get_camera_info()}")
"""

# In your update_video method, replace individual camera reads with:
"""
# Get frames from both cameras
frames = self.camera_manager.read_frames()
critter_frame = frames['critter_cam']
nut_frame = frames['nut_cam']

# Process CritterCam
if critter_frame is not None:
    self.detect_motion(critter_frame, "CritterCam", self.critter_bg_subtractor, 
                     self.critter_last_motion, "critter")
    self.display_frame(critter_frame, self.critter_canvas)

# Process NutCam  
if nut_frame is not None:
    self.detect_motion(nut_frame, "NutCam", self.nut_bg_subtractor,
                     self.nut_last_motion, "nut")
    self.display_frame(nut_frame, self.nut_canvas)
"""

# In your shutdown method, replace camera release with:
"""
self.running = False
self.camera_manager.release()
self.root.quit()
"""

print("Integration example created!")
print("\nKey benefits of using CameraManager:")
print("✅ Clean separation of camera logic")
print("✅ Debug mode for development without hardware")
print("✅ Production-ready error handling")
print("✅ Automatic video looping in debug mode")
print("✅ Context manager support")
print("✅ Comprehensive logging")
print("\nTo switch modes, just change debug_mode in the config!")
