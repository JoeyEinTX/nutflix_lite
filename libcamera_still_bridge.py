#!/usr/bin/env python3
"""
Simplified LibCamera Bridge using libcamera-still
Uses individual frame captures instead of continuous video stream
"""

import subprocess
import numpy as np
import cv2
import threading
import time
import tempfile
import os
from typing import Optional, Tuple
from nutflix_common.logger import get_logger

logger = get_logger("libcamera_still")

class LibCameraStillCapture:
    """
    A camera capture class using libcamera-still for individual frame captures.
    More reliable than streaming video for our use case.
    """
    
    def __init__(self, camera_id: int, width: int = 640, height: int = 480):
        """
        Initialize libcamera-still capture.
        
        Args:
            camera_id: Camera index (0, 1, etc.)
            width: Frame width
            height: Frame height 
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.temp_dir = tempfile.mkdtemp()
        self.frame_count = 0
        self.capture_thread = None
        
        logger.info(f"Initializing libcamera-still capture for camera {camera_id}")
        
    def start(self) -> bool:
        """Start the libcamera capture process."""
        try:
            # Test if camera is accessible
            test_file = os.path.join(self.temp_dir, f"test_cam{self.camera_id}.jpg")
            cmd = [
                '/usr/bin/libcamera-still',
                '--camera', str(self.camera_id),
                '--width', str(self.width),
                '--height', str(self.height),
                '--output', test_file,
                '--timeout', '1000',  # 1 second timeout
                '--nopreview'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.error(f"Camera {self.camera_id} test failed: {result.stderr}")
                return False
            
            if not os.path.exists(test_file):
                logger.error(f"Camera {self.camera_id} test image not created")
                return False
                
            # Clean up test file
            os.remove(test_file)
            
            self.running = True
            
            # Start frame capture thread
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            logger.info(f"LibCamera-still capture started for camera {self.camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start libcamera-still capture: {e}")
            return False
    
    def _capture_loop(self):
        """Main capture loop that takes individual photos."""
        while self.running:
            try:
                # Create temporary file for this frame
                frame_file = os.path.join(self.temp_dir, f"frame_cam{self.camera_id}_{self.frame_count}.jpg")
                
                # Capture frame
                cmd = [
                    '/usr/bin/libcamera-still',
                    '--camera', str(self.camera_id),
                    '--width', str(self.width),
                    '--height', str(self.height),
                    '--output', frame_file,
                    '--timeout', '100',  # 100ms timeout for fast capture
                    '--nopreview'
                ]
                
                result = subprocess.run(cmd, capture_output=True, timeout=2)
                
                if result.returncode == 0 and os.path.exists(frame_file):
                    # Load the image
                    frame = cv2.imread(frame_file)
                    
                    if frame is not None:
                        # Store the frame thread-safely
                        with self.frame_lock:
                            self.current_frame = frame.copy()
                            self.frame_count += 1
                        
                        if self.frame_count % 50 == 0:
                            logger.debug(f"Camera {self.camera_id}: {self.frame_count} frames captured")
                    
                    # Clean up the file
                    try:
                        os.remove(frame_file)
                    except:
                        pass
                else:
                    logger.warning(f"Failed to capture frame from camera {self.camera_id}")
                
                # Small delay between captures (about 10 FPS)
                time.sleep(0.1)
                    
            except Exception as e:
                if self.running:
                    logger.error(f"Error in capture loop: {e}")
                time.sleep(0.5)  # Wait before retrying
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read the latest frame.
        
        Returns:
            Tuple of (success, frame) like OpenCV VideoCapture.read()
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return True, self.current_frame.copy()
            else:
                return False, None
    
    def isOpened(self) -> bool:
        """Check if the capture is running."""
        return self.running
    
    def release(self):
        """Stop the capture and clean up resources."""
        logger.info(f"Releasing libcamera-still capture for camera {self.camera_id}")
        
        self.running = False
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=5)
        
        # Clean up temp directory
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temp directory: {e}")
        
        logger.info(f"LibCamera-still capture released for camera {self.camera_id}")


def test_libcamera_still():
    """Test function for libcamera-still capture."""
    logger.info("Testing LibCamera-still capture...")
    
    # Test camera 0
    cap = LibCameraStillCapture(0, width=640, height=480)
    
    if not cap.start():
        logger.error("Failed to start camera 0")
        return False
    
    # Try to read a few frames
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            logger.info(f"Frame {i}: {frame.shape}")
            time.sleep(0.5)
        else:
            logger.warning(f"Failed to read frame {i}")
    
    cap.release()
    logger.info("LibCamera-still test completed")
    return True


if __name__ == "__main__":
    test_libcamera_still()
