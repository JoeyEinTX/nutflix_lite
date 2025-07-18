#!/usr/bin/env python3
"""
Camera Manager for Nutflix Lite
Handles dual camera inputs for production Raspberry Pi hardware.
"""

import cv2
import time
from typing import Dict, Optional, Any

# Use nutflix_common logger
from nutflix_common.logger import get_camera_logger

# Get logger for this module
logger = get_camera_logger()


class CameraManager:
    """
    Manages camera capture operations for production Raspberry Pi hardware.
    
    This class handles dual camera setup with real hardware cameras.
    """
    
    def __init__(self, config: dict):
        """
        Initialize the camera manager.
        
        Args:
            config: Dictionary containing camera configuration:
                - critter_cam_id: Camera ID for CritterCam (default: 0)
                - nut_cam_id: Camera ID for NutCam (default: 1)
        """
        self.config = config
        self.critter_cam_id = config.get('critter_cam_id', 0)
        self.nut_cam_id = config.get('nut_cam_id', 1)
        
        # Camera capture objects
        self._critter_capture = None
        self._nut_capture = None
        
        logger.info("Initializing CameraManager for hardware cameras")
        
        # Initialize cameras
        self._initialize_cameras()
    
    def _initialize_cameras(self):
        """Initialize hardware camera capture objects."""
        logger.info("Initializing hardware cameras")
        
        # Initialize CritterCam
        try:
            self._critter_capture = cv2.VideoCapture(self.critter_cam_id)
            if not self._critter_capture.isOpened():
                raise RuntimeError(f"Failed to open CritterCam with ID {self.critter_cam_id}")
            logger.info(f"CritterCam initialized successfully (ID: {self.critter_cam_id})")
        except Exception as e:
            logger.error(f"CritterCam initialization failed: {e}")
            raise RuntimeError(f"Cannot initialize CritterCam (ID: {self.critter_cam_id}): {e}")
        
        # Initialize NutCam
        try:
            self._nut_capture = cv2.VideoCapture(self.nut_cam_id)
            if not self._nut_capture.isOpened():
                raise RuntimeError(f"Failed to open NutCam with ID {self.nut_cam_id}")
            logger.info(f"NutCam initialized successfully (ID: {self.nut_cam_id})")
        except Exception as e:
            logger.error(f"NutCam initialization failed: {e}")
            raise RuntimeError(f"Cannot initialize NutCam (ID: {self.nut_cam_id}): {e}")
    
    def _initialize_cameras(self):
        """Initialize hardware camera capture objects."""
        logger.info("Initializing hardware cameras")
        
        # Initialize CritterCam
        try:
            self._critter_capture = cv2.VideoCapture(self.critter_cam_id)
            if not self._critter_capture.isOpened():
                raise RuntimeError(f"Failed to open CritterCam with ID {self.critter_cam_id}")
            logger.info(f"CritterCam initialized successfully (ID: {self.critter_cam_id})")
        except Exception as e:
            logger.error(f"CritterCam initialization failed: {e}")
            raise RuntimeError(f"Cannot initialize CritterCam (ID: {self.critter_cam_id}): {e}")
        
        # Initialize NutCam
        try:
            self._nut_capture = cv2.VideoCapture(self.nut_cam_id)
            if not self._nut_capture.isOpened():
                raise RuntimeError(f"Failed to open NutCam with ID {self.nut_cam_id}")
            logger.info(f"NutCam initialized successfully (ID: {self.nut_cam_id})")
        except Exception as e:
            logger.error(f"NutCam initialization failed: {e}")
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
