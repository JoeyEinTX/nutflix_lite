#!/usr/bin/env python3
"""
LibCamera Bridge for Nutflix
Bridges libcamera to OpenCV for Raspberry Pi cameras
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

logger = get_logger("libcamera")

class LibCameraCapture:
    """
    A wrapper class that uses libcamera to capture frames and makes them available to OpenCV.
    This bridges the gap between libcamera (Pi camera system) and OpenCV.
    """
    
    def __init__(self, camera_id: int, width: int = 640, height: int = 480, fps: int = 30):
        """
        Initialize libcamera capture.
        
        Args:
            camera_id: Camera index (0, 1, etc.)
            width: Frame width
            height: Frame height 
            fps: Frames per second
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.running = False
        self.process = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.temp_dir = tempfile.mkdtemp()
        self.frame_count = 0
        
        logger.info(f"Initializing libcamera capture for camera {camera_id}")
        
    def start(self) -> bool:
        """Start the libcamera capture process."""
        try:
            # Create libcamera-vid command for continuous capture
            # Use absolute path to ensure systemd can find it
            cmd = [
                '/usr/bin/libcamera-vid',
                '--camera', str(self.camera_id),
                '--width', str(self.width),
                '--height', str(self.height),
                '--framerate', str(self.fps),
                '--timeout', '0',  # Run indefinitely
                '--output', '-',   # Output to stdout
                '--codec', 'yuv420',
                '--flush'
            ]
            
            logger.info(f"Starting libcamera process: {' '.join(cmd)}")
            
            # Start the process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            
            self.running = True
            
            # Start frame reading thread
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if process is still running
            if self.process.poll() is not None:
                stderr = self.process.stderr.read().decode()
                logger.error(f"libcamera process failed: {stderr}")
                return False
                
            logger.info(f"LibCamera capture started for camera {self.camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start libcamera capture: {e}")
            return False
    
    def _capture_loop(self):
        """Main capture loop that reads frames from libcamera."""
        frame_size = self.width * self.height * 3 // 2  # YUV420 format
        
        while self.running and self.process and self.process.poll() is None:
            try:
                # Read YUV420 frame data
                yuv_data = self.process.stdout.read(frame_size)
                
                if len(yuv_data) != frame_size:
                    logger.warning(f"Incomplete frame read: {len(yuv_data)}/{frame_size}")
                    continue
                
                # Convert YUV420 to BGR for OpenCV
                yuv_array = np.frombuffer(yuv_data, dtype=np.uint8)
                yuv_frame = yuv_array.reshape((self.height * 3 // 2, self.width))
                
                # Convert YUV to BGR
                bgr_frame = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2BGR_I420)
                
                # Store the frame thread-safely
                with self.frame_lock:
                    self.current_frame = bgr_frame.copy()
                    self.frame_count += 1
                
                if self.frame_count % 100 == 0:
                    logger.debug(f"Camera {self.camera_id}: {self.frame_count} frames captured")
                    
            except Exception as e:
                if self.running:
                    logger.error(f"Error in capture loop: {e}")
                break
    
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
        return self.running and self.process and self.process.poll() is None
    
    def release(self):
        """Stop the capture and clean up resources."""
        logger.info(f"Releasing libcamera capture for camera {self.camera_id}")
        
        self.running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Force killing libcamera process")
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logger.error(f"Error stopping libcamera process: {e}")
        
        # Clean up temp directory
        try:
            os.rmdir(self.temp_dir)
        except:
            pass
        
        logger.info(f"LibCamera capture released for camera {self.camera_id}")


def test_libcamera_capture():
    """Test function for libcamera capture."""
    logger.info("Testing LibCamera capture...")
    
    # Test camera 0
    cap = LibCameraCapture(0, width=640, height=480, fps=10)
    
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
    logger.info("LibCamera test completed")
    return True


if __name__ == "__main__":
    test_libcamera_capture()
