#!/usr/bin/env python3
"""
Camera Manager for Nutflix Lite
Handles dual camera inputs for production Raspberry Pi hardware.
"""

import cv2
import time
import threading
from typing import Dict, Optional, Any

from nutflix_common.logger import get_camera_logger

try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except (ImportError, ValueError):
    PICAMERA2_AVAILABLE = False

try:
    from libcamera_still_bridge import LibCameraStillCapture
    LIBCAMERA_AVAILABLE = True
except ImportError:
    LIBCAMERA_AVAILABLE = False

logger = get_camera_logger()

class CameraManager:
    def __init__(self, config: dict, status_callback=None):
        self.config = config
        self.critter_cam_id = config.get('critter_cam_id', 0)
        self.nut_cam_id = config.get('nut_cam_id', 1)
        self.status_callback = status_callback

        self._critter_capture = None
        self._nut_capture = None

        self._latest_frames = {'critter_cam': None, 'nut_cam': None}
        self._capture_threads = {}

        # Always use Picamera2 for dual camera setup
        self._initialize_cameras()

    def _initialize_cameras(self):
        """Initialize cameras using Picamera2 only."""
        if PICAMERA2_AVAILABLE:
            self._initialize_picamera2()
        else:
            raise RuntimeError("Picamera2 is required but not available. Please install picamera2.")
        
        # Fallback methods removed - we always use Picamera2 for Pi dual camera setup
        # elif self._use_libcamera and LIBCAMERA_AVAILABLE:
        #     self._initialize_libcamera()
        # else:
        #     self._initialize_opencv()

    def _initialize_picamera2(self):
        try:
            self._critter_capture = Picamera2(camera_num=self.critter_cam_id)
            config0 = self._critter_capture.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
            self._critter_capture.configure(config0)
            self._critter_capture.start()
            self._start_capture_thread('critter_cam', self._critter_capture)

            if self.status_callback:
                self.status_callback('critter_cam', 'Ready')

            self._nut_capture = Picamera2(camera_num=self.nut_cam_id)
            config1 = self._nut_capture.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
            self._nut_capture.configure(config1)
            self._nut_capture.start()
            self._start_capture_thread('nut_cam', self._nut_capture)

            if self.status_callback:
                self.status_callback('nut_cam', 'Ready')
        except Exception as e:
            logger.error(f"Picamera2 initialization failed: {e}")
            raise

    # Removed fallback methods - we only support Picamera2 for Pi dual camera setup
    # def _initialize_libcamera(self):
    # def _initialize_opencv(self):

    def _start_capture_thread(self, cam_name, capture):
        """Start capture thread for Picamera2 only."""
        def capture_loop():
            while True:
                try:
                    # Picamera2 capture only
                    frame = capture.capture_array()
                    if frame is not None:
                        self._latest_frames[cam_name] = frame
                    time.sleep(0.05)
                except Exception as e:
                    logger.error(f"Frame loop error for {cam_name}: {e}")
                    break
        t = threading.Thread(target=capture_loop, daemon=True)
        self._capture_threads[cam_name] = t
        t.start()

    def get_latest_frame(self, camera_name: str) -> Optional[bytes]:
        """Get the latest frame from a camera as JPEG bytes (Picamera2 only)."""
        try:
            frame = self._latest_frames.get(camera_name)
            if frame is None:
                return None

            # Picamera2 returns RGB888 format, convert to JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            return buffer.tobytes() if ret else None
        except Exception as e:
            logger.error(f"Error encoding frame from {camera_name}: {e}")
            return None

    def is_camera_available(self, camera_name: str) -> bool:
        """Check if a camera is available and ready."""
        try:
            if camera_name == 'critter_cam':
                return self._critter_capture is not None and camera_name in self._latest_frames
            elif camera_name == 'nut_cam':
                return self._nut_capture is not None and camera_name in self._latest_frames
            else:
                return False
        except Exception as e:
            logger.error(f"Error checking camera availability for {camera_name}: {e}")
            return False

    def get_camera_info(self) -> Dict[str, Any]:
        """Get information about available cameras (Picamera2 only)."""
        try:
            info = {
                'critter_cam': {
                    'id': self.critter_cam_id,
                    'available': self.is_camera_available('critter_cam'),
                    'status': 'Ready' if self.is_camera_available('critter_cam') else 'Not Available'
                },
                'nut_cam': {
                    'id': self.nut_cam_id,
                    'available': self.is_camera_available('nut_cam'),
                    'status': 'Ready' if self.is_camera_available('nut_cam') else 'Not Available'
                },
                'backend': 'Picamera2',  # Always Picamera2 now
                'total_cameras': 2
            }
            return info
        except Exception as e:
            logger.error(f"Error getting camera info: {e}")
            return {'error': str(e)}

    def cleanup(self):
        """Clean up Picamera2 resources."""
        logger.info("Cleaning up camera resources")
        if self._critter_capture:
            try:
                # Picamera2 cleanup
                self._critter_capture.stop()
                self._critter_capture.close()
            except Exception as e:
                logger.error(f"Error releasing CritterCam: {e}")
        if self._nut_capture:
            try:
                # Picamera2 cleanup
                self._nut_capture.stop()
                self._nut_capture.close()
            except Exception as e:
                logger.error(f"Error releasing NutCam: {e}")
