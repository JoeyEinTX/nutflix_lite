#!/usr/bin/env python3
"""
Camera Manager for Nutflix Lite
Handles dual camera inputs with hardware/debug mode support
"""

import cv2
import os
from typing import Dict, Optional, Any

# Use nutflix_common logger
from nutflix_common.logger import get_camera_logger

# Get logger for this module
logger = get_camera_logger()


class CameraManager:
    """
    Production-ready camera manager for Nutflix Lite dual-camera setup.
    Supports both hardware cameras (Raspberry Pi) and debug mode with video files.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the camera manager with configuration.
        
        Args:
            config: Dictionary containing:
                - critter_cam_id: Camera ID for CritterCam (default: 0)
                - nut_cam_id: Camera ID for NutCam (default: 1)
                - debug_mode: Boolean flag for debug mode (default: False)
        """
        self.config = config
        self.debug_mode = config.get('debug_mode', False)
        self.critter_cam_id = config.get('critter_cam_id', 0)
        self.nut_cam_id = config.get('nut_cam_id', 1)
        
        # Camera capture objects
        self._critter_capture = None
        self._nut_capture = None
        
        # Video file paths for debug mode
        self._critter_video_path = "sample_clips/crittercam.mp4"
        self._nut_video_path = "sample_clips/nutcam.mp4"
        
        logger.info(f"Initializing CameraManager - Debug mode: {self.debug_mode}")
        
        # Initialize cameras
        self._initialize_cameras()
    
    def _initialize_cameras(self):
        """Initialize camera capture objects based on mode."""
        if self.debug_mode:
            self._initialize_debug_cameras()
        else:
            self._initialize_hardware_cameras()
    
    def _initialize_debug_cameras(self):
        """Initialize cameras in debug mode using video files."""
        logger.info("Initializing debug mode cameras with video files")
        
        # Initialize CritterCam with video file
        if os.path.exists(self._critter_video_path):
            self._critter_capture = cv2.VideoCapture(self._critter_video_path)
            if self._critter_capture.isOpened():
                logger.info(f"CritterCam debug video loaded: {self._critter_video_path}")
            else:
                logger.warning(f"Failed to open CritterCam debug video: {self._critter_video_path}")
                self._critter_capture = None
        else:
            logger.warning(f"CritterCam debug video file not found: {self._critter_video_path}")
            self._critter_capture = None
        
        # Initialize NutCam with video file
        if os.path.exists(self._nut_video_path):
            self._nut_capture = cv2.VideoCapture(self._nut_video_path)
            if self._nut_capture.isOpened():
                logger.info(f"NutCam debug video loaded: {self._nut_video_path}")
            else:
                logger.warning(f"Failed to open NutCam debug video: {self._nut_video_path}")
                self._nut_capture = None
        else:
            logger.warning(f"NutCam debug video file not found: {self._nut_video_path}")
            self._nut_capture = None
    
    def _initialize_hardware_cameras(self):
        """Initialize hardware cameras for production use."""
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
                    # Handle video loop for debug mode
                    if self.debug_mode and self._critter_capture:
                        self._critter_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self._critter_capture.read()
                        if ret and frame is not None:
                            frames['critter_cam'] = frame
                        else:
                            logger.warning("CritterCam frame read failed even after loop reset")
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
                    # Handle video loop for debug mode
                    if self.debug_mode and self._nut_capture:
                        self._nut_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self._nut_capture.read()
                        if ret and frame is not None:
                            frames['nut_cam'] = frame
                        else:
                            logger.warning("NutCam frame read failed even after loop reset")
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
            'debug_mode': self.debug_mode,
            'critter_cam': {
                'id': self.critter_cam_id if not self.debug_mode else self._critter_video_path,
                'available': self.is_camera_available('critter_cam'),
                'type': 'video_file' if self.debug_mode else 'hardware'
            },
            'nut_cam': {
                'id': self.nut_cam_id if not self.debug_mode else self._nut_video_path,
                'available': self.is_camera_available('nut_cam'),
                'type': 'video_file' if self.debug_mode else 'hardware'
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
    # Test configuration for debug mode
    debug_config = {
        'debug_mode': True,
        'critter_cam_id': 0,
        'nut_cam_id': 1
    }
    
    # Test configuration for hardware mode
    hardware_config = {
        'debug_mode': False,
        'critter_cam_id': 0,
        'nut_cam_id': 1
    }
    
    print("Testing CameraManager...")
    
    # Test with context manager (recommended usage)
    try:
        with CameraManager(debug_config) as cam_manager:
            print(f"Camera info: {cam_manager.get_camera_info()}")
            
            # Read a few frames to test
            for i in range(3):
                frames = cam_manager.read_frames()
                critter_frame = frames['critter_cam']
                nut_frame = frames['nut_cam']
                
                print(f"Frame {i+1}:")
                print(f"  CritterCam: {'✓' if critter_frame is not None else '✗'}")
                print(f"  NutCam: {'✓' if nut_frame is not None else '✗'}")
        
        print("CameraManager test completed successfully!")
        
    except Exception as e:
        print(f"CameraManager test failed: {e}")
