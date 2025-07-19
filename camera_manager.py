#!/usr/bin/env python3
"""
Camera Manager for Nutflix Lite
Handles dual camera inputs for production Raspberry Pi hardware.
"""

import cv2
import time
import platform
from typing import Dict, Optional, Any

# Use nutflix_common logger
from nutflix_common.logger import get_camera_logger

# Import libcamera bridge for Raspberry Pi
try:
    from libcamera_still_bridge import LibCameraStillCapture
    LIBCAMERA_AVAILABLE = True
except ImportError:
    LIBCAMERA_AVAILABLE = False

# Get logger for this module
logger = get_camera_logger()


class CameraManager:
    """
    Manages camera capture operations for production Raspberry Pi hardware.
    
    This class handles dual camera setup with real hardware cameras.
    Uses libcamera bridge on Raspberry Pi for better camera compatibility.
    """
    
    def __init__(self, config: dict, status_callback=None):
        """
        Initialize the camera manager.
        
        Args:
            config: Dictionary containing camera configuration:
                - critter_cam_id: Camera ID for CritterCam (default: 0)
                - nut_cam_id: Camera ID for NutCam (default: 1)
            status_callback: Optional callback function for status updates
        """
        self.config = config
        self.critter_cam_id = config.get('critter_cam_id', 0)
        self.nut_cam_id = config.get('nut_cam_id', 1)
        self.status_callback = status_callback
        
        # Camera capture objects
        self._critter_capture = None
        self._nut_capture = None
        
        # Detect if we're on Raspberry Pi
        self._is_raspberry_pi = self._detect_raspberry_pi()
        self._use_libcamera = self._is_raspberry_pi and LIBCAMERA_AVAILABLE
        
        logger.info(f"Initializing CameraManager for hardware cameras")
        logger.info(f"Platform: {'Raspberry Pi' if self._is_raspberry_pi else 'Other'}")
        logger.info(f"Using libcamera: {self._use_libcamera}")
        
        # Initialize cameras
        self._initialize_cameras()
    
    def _detect_raspberry_pi(self) -> bool:
        """Detect if we're running on a Raspberry Pi."""
        try:
            # Check /proc/cpuinfo for Raspberry Pi indicators
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read().lower()
                if 'raspberry pi' in cpuinfo or 'bcm' in cpuinfo:
                    return True
            
            # Check /proc/device-tree/model
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    model = f.read().lower()
                    if 'raspberry pi' in model:
                        return True
            except:
                pass
            
            # Check platform
            import platform
            machine = platform.machine().lower()
            if 'arm' in machine or 'aarch64' in machine:
                # Additional check for Pi-specific paths
                import os
                if os.path.exists('/opt/vc') or os.path.exists('/usr/bin/libcamera-hello'):
                    return True
            
            return False
        except Exception as e:
            logger.warning(f"Pi detection failed: {e}")
            return False
    
    def _initialize_cameras(self):
        """Initialize hardware camera capture objects."""
        logger.info("Initializing hardware cameras")
        
        if self._use_libcamera:
            logger.info("Using libcamera bridge for Raspberry Pi cameras")
            self._initialize_libcamera()
        else:
            logger.info("Using OpenCV VideoCapture")
            self._initialize_opencv()
    
    def _initialize_libcamera(self):
        """Initialize cameras using libcamera-still bridge."""
        # Initialize CritterCam
        try:
            self._critter_capture = LibCameraStillCapture(self.critter_cam_id, width=640, height=480)
            if not self._critter_capture.start():
                raise RuntimeError(f"Failed to start CritterCam with ID {self.critter_cam_id}")
            logger.info(f"CritterCam initialized with libcamera-still (ID: {self.critter_cam_id})")
            
            # Emit status update for CritterCam
            if self.status_callback:
                self.status_callback('critter_cam', 'Ready')
                
        except Exception as e:
            logger.error(f"CritterCam libcamera initialization failed: {e}")
            if self.status_callback:
                self.status_callback('critter_cam', 'Error')
            raise RuntimeError(f"Cannot initialize CritterCam (ID: {self.critter_cam_id}): {e}")
        
        # Initialize NutCam
        try:
            self._nut_capture = LibCameraStillCapture(self.nut_cam_id, width=640, height=480)
            if not self._nut_capture.start():
                raise RuntimeError(f"Failed to start NutCam with ID {self.nut_cam_id}")
            logger.info(f"NutCam initialized with libcamera-still (ID: {self.nut_cam_id})")
            
            # Emit status update for NutCam
            if self.status_callback:
                self.status_callback('nut_cam', 'Ready')
                
        except Exception as e:
            logger.error(f"NutCam libcamera initialization failed: {e}")
            if self.status_callback:
                self.status_callback('nut_cam', 'Error')
            raise RuntimeError(f"Cannot initialize NutCam (ID: {self.nut_cam_id}): {e}")
    
    def _initialize_opencv(self):
        """Initialize cameras using OpenCV VideoCapture."""
        # Initialize CritterCam
        try:
            self._critter_capture = cv2.VideoCapture(self.critter_cam_id)
            if not self._critter_capture.isOpened():
                raise RuntimeError(f"Failed to open CritterCam with ID {self.critter_cam_id}")
            logger.info(f"CritterCam initialized successfully (ID: {self.critter_cam_id})")
            
            # Emit status update for CritterCam
            if self.status_callback:
                self.status_callback('critter_cam', 'Ready')
                
        except Exception as e:
            logger.error(f"CritterCam initialization failed: {e}")
            if self.status_callback:
                self.status_callback('critter_cam', 'Error')
            raise RuntimeError(f"Cannot initialize CritterCam (ID: {self.critter_cam_id}): {e}")
        
        # Initialize NutCam
        try:
            self._nut_capture = cv2.VideoCapture(self.nut_cam_id)
            if not self._nut_capture.isOpened():
                raise RuntimeError(f"Failed to open NutCam with ID {self.nut_cam_id}")
            logger.info(f"NutCam initialized successfully (ID: {self.nut_cam_id})")
            
            # Emit status update for NutCam
            if self.status_callback:
                self.status_callback('nut_cam', 'Ready')
                
        except Exception as e:
            logger.error(f"NutCam initialization failed: {e}")
            if self.status_callback:
                self.status_callback('nut_cam', 'Error')
            raise RuntimeError(f"Cannot initialize NutCam (ID: {self.nut_cam_id}): {e}")
    
    def read_frames(self) -> Dict[str, Optional[Any]]:
        """
        Read one frame from each camera.
        
        Returns:
            Dictionary with keys 'critter_cam' and 'nut_cam'.
            Values are OpenCV frame arrays or None if read failed.
        """
        frames = {
            'critter_cam': None,
            'nut_cam': None
        }
        
        # Read CritterCam frame
        if self._critter_capture and self._critter_capture.isOpened():
            try:
                ret, frame = self._critter_capture.read()
                if ret and frame is not None:
                    frames['critter_cam'] = frame
                else:
                    logger.warning("CritterCam frame read failed")
            except Exception as e:
                logger.error(f"Error reading CritterCam frame: {e}")
        
        # Read NutCam frame
        if self._nut_capture and self._nut_capture.isOpened():
            try:
                ret, frame = self._nut_capture.read()
                if ret and frame is not None:
                    frames['nut_cam'] = frame
                else:
                    logger.warning("NutCam frame read failed")
            except Exception as e:
                logger.error(f"Error reading NutCam frame: {e}")
        
        return frames
    
    def release(self):
        """Release all camera capture objects and clean up resources."""
        logger.info("Releasing camera resources")
        
        if self._critter_capture:
            try:
                self._critter_capture.release()
                logger.info("CritterCam released successfully")
            except Exception as e:
                logger.error(f"Error releasing CritterCam: {e}")
            finally:
                self._critter_capture = None
        
        if self._nut_capture:
            try:
                self._nut_capture.release()
                logger.info("NutCam released successfully")
            except Exception as e:
                logger.error(f"Error releasing NutCam: {e}")
            finally:
                self._nut_capture = None
    
    def is_camera_available(self, camera_name: str) -> bool:
        """
        Check if a specific camera is available and operational.
        
        Args:
            camera_name: Either 'critter_cam' or 'nut_cam'
            
        Returns:
            True if camera is available, False otherwise
        """
        if camera_name == 'critter_cam':
            return self._critter_capture is not None and self._critter_capture.isOpened()
        elif camera_name == 'nut_cam':
            return self._nut_capture is not None and self._nut_capture.isOpened()
        else:
            logger.warning(f"Unknown camera name: {camera_name}")
            return False
    
    def get_camera_info(self) -> Dict[str, Any]:
        """
        Get information about the current camera configuration.
        
        Returns:
            Dictionary with camera configuration and status information
        """
        return {
            'critter_cam': {
                'id': self.critter_cam_id,
                'available': self.is_camera_available('critter_cam'),
                'type': 'hardware'
            },
            'nut_cam': {
                'id': self.nut_cam_id,
                'available': self.is_camera_available('nut_cam'),
                'type': 'hardware'
            }
        }
    
    def cleanup(self):
        """Clean up resources and release cameras."""
        logger.info("Cleaning up camera resources...")
        self.release()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically release resources."""
        self.release()


# Example usage and testing
if __name__ == "__main__":
    # Test configuration for hardware cameras
    hardware_config = {
        'critter_cam_id': 0,
        'nut_cam_id': 1
    }
    
    print("Testing CameraManager...")
    
    # Test with context manager (recommended usage)
    try:
        with CameraManager(hardware_config) as cam_manager:
            print(f"Camera info: {cam_manager.get_camera_info()}")
            
            # Read a few frames to test
            for i in range(5):
                frames = cam_manager.read_frames()
                print(f"Frame {i+1}:")
                print(f"  CritterCam: {'OK' if frames['critter_cam'] is not None else 'Failed'}")
                print(f"  NutCam: {'OK' if frames['nut_cam'] is not None else 'Failed'}")
                
                if frames['critter_cam'] is not None:
                    print(f"  CritterCam shape: {frames['critter_cam'].shape}")
                if frames['nut_cam'] is not None:
                    print(f"  NutCam shape: {frames['nut_cam'].shape}")
                
                time.sleep(0.1)  # Small delay between frames
                
    except Exception as e:
        print(f"Error during camera testing: {e}")
    
    print("Camera testing completed")
