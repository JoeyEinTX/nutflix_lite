#!/usr/bin/env python3
"""
Motion Detection Utilities for Nutflix Common
Handles motion detection logic using OpenCV background subtraction
"""

import cv2
import numpy as np
import time
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass, field

# Use nutflix_common logger
from .logger import get_motion_logger

# Get logger for this module
logger = get_motion_logger()


@dataclass
class MotionEvent:
    """Data class to represent a motion detection event."""
    camera_id: str
    timestamp: float
    contour_count: int
    largest_contour_area: float
    frame_shape: Tuple[int, int]


@dataclass
class MotionConfig:
    """Configuration for motion detection parameters."""
    threshold: int = 500              # Minimum contour area to consider as motion
    sensitivity: int = 25             # Threshold for frame difference (unused in MOG2 but kept for compatibility)
    cooldown: float = 2.0            # Seconds between motion logs for same camera
    gaussian_blur_kernel: Tuple[int, int] = (21, 21)  # Gaussian blur kernel size
    gaussian_blur_sigma: int = 0      # Gaussian blur sigma
    mog2_detect_shadows: bool = True  # Whether to detect shadows in MOG2
    mog2_history: int = 500          # Number of frames in MOG2 history
    mog2_var_threshold: float = 16.0  # MOG2 variance threshold
    min_contour_area: int = 100      # Minimum contour area to consider
    max_contours_to_check: int = 50   # Maximum number of contours to process


class MotionDetector:
    """
    Production-ready motion detector using OpenCV background subtraction.
    Supports multiple cameras with independent motion tracking and cooldown.
    """
    
    def __init__(self, config: Optional[MotionConfig] = None):
        """
        Initialize the motion detector.
        
        Args:
            config: Motion detection configuration. Uses defaults if None.
        """
        self.config = config or MotionConfig()
        
        # Background subtractors for each camera
        self._bg_subtractors: Dict[str, cv2.BackgroundSubtractor] = {}
        
        # Motion tracking per camera
        self._last_motion_times: Dict[str, float] = {}
        self._motion_events: Dict[str, list] = {}
        
        # Frame processing stats
        self._frame_counts: Dict[str, int] = {}
        
        logger.info(f"MotionDetector initialized with threshold={self.config.threshold}, "
                   f"cooldown={self.config.cooldown}s")
    
    def _get_or_create_bg_subtractor(self, camera_id: str) -> cv2.BackgroundSubtractor:
        """Get or create a background subtractor for the given camera."""
        if camera_id not in self._bg_subtractors:
            self._bg_subtractors[camera_id] = cv2.createBackgroundSubtractorMOG2(
                history=self.config.mog2_history,
                varThreshold=self.config.mog2_var_threshold,
                detectShadows=self.config.mog2_detect_shadows
            )
            self._last_motion_times[camera_id] = 0
            self._motion_events[camera_id] = []
            self._frame_counts[camera_id] = 0
            logger.info(f"Created background subtractor for camera: {camera_id}")
        
        return self._bg_subtractors[camera_id]
    
    def process_frame(self, frame: np.ndarray, camera_id: str) -> bool:
        """
        Process a frame for motion detection.
        
        Args:
            frame: OpenCV frame (BGR format)
            camera_id: Unique identifier for the camera
            
        Returns:
            True if motion was detected, False otherwise
        """
        if frame is None:
            logger.warning(f"Received None frame for camera {camera_id}")
            return False
        
        current_time = time.time()
        self._frame_counts[camera_id] = self._frame_counts.get(camera_id, 0) + 1
        
        # Check cooldown period
        if self._is_in_cooldown(camera_id, current_time):
            return False
        
        try:
            # Get background subtractor for this camera
            bg_subtractor = self._get_or_create_bg_subtractor(camera_id)
            
            # Preprocess frame
            processed_frame = self._preprocess_frame(frame)
            
            # Apply background subtraction
            fg_mask = bg_subtractor.apply(processed_frame)
            
            # Find and analyze contours
            motion_detected, contour_info = self._analyze_contours(fg_mask)
            
            # Log motion event if detected
            if motion_detected:
                self._record_motion_event(camera_id, current_time, contour_info, frame.shape)
                logger.info(f"Motion detected in {camera_id}: {contour_info['count']} contours, "
                           f"largest area: {contour_info['largest_area']:.1f}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing frame for camera {camera_id}: {e}")
            return False
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for motion detection."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(
            gray, 
            self.config.gaussian_blur_kernel, 
            self.config.gaussian_blur_sigma
        )
        
        return blurred
    
    def _analyze_contours(self, fg_mask: np.ndarray) -> Tuple[bool, Dict[str, Any]]:
        """
        Analyze contours in the foreground mask.
        
        Returns:
            Tuple of (motion_detected, contour_info_dict)
        """
        # Find contours
        contours, _ = cv2.findContours(
            fg_mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        if not contours:
            return False, {'count': 0, 'largest_area': 0}
        
        # Limit number of contours to process for performance
        contours = contours[:self.config.max_contours_to_check]
        
        # Filter contours by area
        valid_contours = []
        areas = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= self.config.min_contour_area:
                valid_contours.append(contour)
                areas.append(area)
        
        if not valid_contours:
            return False, {'count': 0, 'largest_area': 0}
        
        # Check if any contour exceeds the motion threshold
        largest_area = max(areas)
        motion_detected = largest_area >= self.config.threshold
        
        contour_info = {
            'count': len(valid_contours),
            'largest_area': largest_area,
            'total_area': sum(areas),
            'average_area': sum(areas) / len(areas) if areas else 0
        }
        
        return motion_detected, contour_info
    
    def _is_in_cooldown(self, camera_id: str, current_time: float) -> bool:
        """Check if camera is in cooldown period."""
        last_motion_time = self._last_motion_times.get(camera_id, 0)
        return (current_time - last_motion_time) < self.config.cooldown
    
    def _record_motion_event(self, camera_id: str, timestamp: float, 
                           contour_info: Dict[str, Any], frame_shape: Tuple[int, ...]) -> None:
        """Record a motion detection event."""
        event = MotionEvent(
            camera_id=camera_id,
            timestamp=timestamp,
            contour_count=contour_info['count'],
            largest_contour_area=contour_info['largest_area'],
            frame_shape=(frame_shape[1], frame_shape[0])  # (width, height)
        )
        
        self._motion_events[camera_id].append(event)
        self._last_motion_times[camera_id] = timestamp
        
        # Keep only recent events (last 100 per camera)
        if len(self._motion_events[camera_id]) > 100:
            self._motion_events[camera_id] = self._motion_events[camera_id][-100:]
    
    def was_motion_detected(self, camera_id: str, within_seconds: float = 5.0) -> bool:
        """
        Check if motion was detected for a camera within the specified time.
        
        Args:
            camera_id: Camera identifier
            within_seconds: Time window to check for motion
            
        Returns:
            True if motion was detected within the time window
        """
        last_motion_time = self._last_motion_times.get(camera_id, 0)
        return (time.time() - last_motion_time) <= within_seconds
    
    def get_motion_events(self, camera_id: str, since_timestamp: Optional[float] = None) -> list:
        """
        Get motion events for a camera.
        
        Args:
            camera_id: Camera identifier
            since_timestamp: Only return events after this timestamp (optional)
            
        Returns:
            List of MotionEvent objects
        """
        events = self._motion_events.get(camera_id, [])
        
        if since_timestamp is not None:
            events = [event for event in events if event.timestamp >= since_timestamp]
        
        return events
    
    def get_camera_stats(self, camera_id: str) -> Dict[str, Any]:
        """
        Get statistics for a camera.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Dictionary with camera statistics
        """
        events = self._motion_events.get(camera_id, [])
        frame_count = self._frame_counts.get(camera_id, 0)
        last_motion = self._last_motion_times.get(camera_id, 0)
        
        return {
            'camera_id': camera_id,
            'frames_processed': frame_count,
            'motion_events_count': len(events),
            'last_motion_timestamp': last_motion,
            'last_motion_ago_seconds': time.time() - last_motion if last_motion > 0 else None,
            'has_background_subtractor': camera_id in self._bg_subtractors,
            'is_in_cooldown': self._is_in_cooldown(camera_id, time.time())
        }
    
    def reset_camera(self, camera_id: str) -> None:
        """Reset motion detection state for a camera."""
        if camera_id in self._bg_subtractors:
            del self._bg_subtractors[camera_id]
        
        self._last_motion_times.pop(camera_id, None)
        self._motion_events.pop(camera_id, None)
        self._frame_counts.pop(camera_id, None)
        
        logger.info(f"Reset motion detection state for camera: {camera_id}")
    
    def reset_all(self) -> None:
        """Reset motion detection state for all cameras."""
        self._bg_subtractors.clear()
        self._last_motion_times.clear()
        self._motion_events.clear()
        self._frame_counts.clear()
        
        logger.info("Reset motion detection state for all cameras")
    
    def update_config(self, new_config: MotionConfig) -> None:
        """
        Update motion detection configuration.
        Note: Existing background subtractors will need to be recreated.
        """
        self.config = new_config
        # Clear existing subtractors so they get recreated with new config
        self._bg_subtractors.clear()
        logger.info(f"Updated motion detection config: threshold={self.config.threshold}, "
                   f"cooldown={self.config.cooldown}s")


# Convenience functions for simple use cases
def create_motion_detector(threshold: int = 500, cooldown: float = 2.0) -> MotionDetector:
    """
    Create a motion detector with simple configuration.
    
    Args:
        threshold: Minimum contour area for motion detection
        cooldown: Seconds between motion detections for same camera
        
    Returns:
        Configured MotionDetector instance
    """
    config = MotionConfig(threshold=threshold, cooldown=cooldown)
    return MotionDetector(config)


# Example usage and testing
if __name__ == "__main__":
    # Test the motion detector
    print("Testing MotionDetector...")
    
    # Create motion detector with custom config
    config = MotionConfig(threshold=300, cooldown=1.0)
    detector = MotionDetector(config)
    
    # Simulate some frames (in real use, these would be camera frames)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Test processing frames
    for i in range(5):
        motion = detector.process_frame(fake_frame, "test_camera")
        print(f"Frame {i+1}: Motion detected = {motion}")
        
        # Get stats
        stats = detector.get_camera_stats("test_camera")
        print(f"  Stats: {stats['frames_processed']} frames, "
              f"{stats['motion_events_count']} motion events")
        
        time.sleep(0.1)  # Small delay
    
    print("MotionDetector test completed!")
