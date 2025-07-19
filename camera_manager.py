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

        self._use_libcamera = LIBCAMERA_AVAILABLE

        self._initialize_cameras()

    def _initialize_cameras(self):
        if self._use_libcamera and PICAMERA2_AVAILABLE:
            self._initialize_picamera2()
        elif self._use_libcamera and LIBCAMERA_AVAILABLE:
            self._initialize_libcamera()
        else:
            self._initialize_opencv()

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

    def _start_capture_thread(self, cam_name, capture):
        def capture_loop():
            while True:
                try:
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
        try:
            frame = self._latest_frames.get(camera_name)
            if frame is None:
                return None

            frame_rgb = frame if PICAMERA2_AVAILABLE else cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ret, buffer = cv2.imencode('.jpg', frame_rgb, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            return buffer.tobytes() if ret else None
        except Exception as e:
            logger.error(f"Error encoding frame from {camera_name}: {e}")
            return None

    def cleanup(self):
        logger.info("Cleaning up camera resources")
        if self._critter_capture:
            try:
                self._critter_capture.stop()
                self._critter_capture.close()
            except Exception as e:
                logger.error(f"Error releasing CritterCam: {e}")
        if self._nut_capture:
            try:
                self._nut_capture.stop()
                self._nut_capture.close()
            except Exception as e:
                logger.error(f"Error releasing NutCam: {e}")
