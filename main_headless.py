#!/usr/bin/env python3
"""
Nutflix Lite - Headless Camera System
Runs the camera system without GUI, perfect for Raspberry Pi deployment.
Integrates with web dashboard for monitoring.
"""

import time
import threading
import signal
import sys
from typing import Optional

# Import from our nutflix_common package
from nutflix_common.config_loader import load_config
from nutflix_common.motion_utils import MotionDetector, MotionConfig
from nutflix_common.logger import get_logger, configure_from_config
from camera_manager import CameraManager
from status_manager import update_camera_status

class NutflixHeadless:
    """Headless version of Nutflix Lite for Raspberry Pi deployment."""
    
    def __init__(self, config_path="config.yaml"):
        """Initialize the headless camera system."""
        self.logger = get_logger("headless")
        self.running = False
        self.camera_manager: Optional[CameraManager] = None
        self.motion_detector: Optional[MotionDetector] = None
        
        # Load configuration
        try:
            self.config = load_config(config_path)
            self.logger.info(f"Configuration loaded from: {config_path}")
            
            # Configure logging from config
            configure_from_config(self.config)
            self.logger.info("Logging configured from config file")
            
        except Exception as e:
            # Fallback to default config if loading fails
            self.config = self._get_default_config()
            self.logger.warning(f"Config loading failed, using defaults: {e}")
        
        # Extract configuration values
        self.app_config = self.config.get('app_name', 'Nutflix Lite')
        self.motion_config_dict = self.config.get('motion_detection', {})
        self.camera_config = self.config.get('cameras', {})
        
        self.logger.info(f"Starting {self.app_config} in headless mode")
        
        # Initialize components
        self._initialize_camera_manager()
        self._initialize_motion_detector()
        
    def _get_default_config(self):
        """Fallback configuration if config file loading fails."""
        return {
            'app_name': 'Nutflix Lite',
            'cameras': {
                'critter_cam_id': 0,
                'nut_cam_id': 1
            },
            'motion_detection': {
                'threshold': 500,
                'sensitivity': 25,
                'cooldown': 2.0
            }
        }
    
    def _initialize_camera_manager(self):
        """Initialize the camera manager."""
        try:
            # Define status callback for camera updates
            def camera_status_callback(camera_name: str, status: str):
                self.logger.info(f"{camera_name} status update: {status}")
                update_camera_status(camera_name, status)
            
            self.camera_manager = CameraManager(self.camera_config, camera_status_callback)
            camera_info = self.camera_manager.get_camera_info()
            self.logger.info(f"Camera system: {camera_info['critter_cam']['type']} mode")
            self.logger.info(f"CritterCam: {'✓' if camera_info['critter_cam']['available'] else '✗'}")
            self.logger.info(f"NutCam: {'✓' if camera_info['nut_cam']['available'] else '✗'}")
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
            self.camera_manager = None
            raise
    
    def _initialize_motion_detector(self):
        """Initialize the motion detector."""
        motion_config = MotionConfig(
            threshold=self.motion_config_dict.get('threshold', 500),
            sensitivity=self.motion_config_dict.get('sensitivity', 25),
            cooldown=self.motion_config_dict.get('cooldown', 2.0)
        )
        self.motion_detector = MotionDetector(motion_config)
        self.logger.info(f"Motion detector initialized: threshold={motion_config.threshold}, cooldown={motion_config.cooldown}s")
    
    def start(self):
        """Start the headless camera system."""
        if not self.camera_manager:
            self.logger.error("Cannot start: camera manager not initialized")
            return False
        
        self.running = True
        self.logger.info("Starting headless camera monitoring...")
        
        # Start the main monitoring loop in a separate thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        return True
    
    def _monitor_loop(self):
        """Main monitoring loop - processes camera frames and detects motion."""
        frame_count = 0
        start_time = time.time()
        
        while self.running:
            try:
                # Get frames from both cameras
                frames = self.camera_manager.read_frames()
                critter_frame = frames['critter_cam']
                nut_frame = frames['nut_cam']
                
                # Process CritterCam
                if critter_frame is not None:
                    motion_detected = self.motion_detector.process_frame(critter_frame, "critter_cam")
                    if motion_detected:
                        self._log_motion_event("CritterCam")
                
                # Process NutCam  
                if nut_frame is not None:
                    motion_detected = self.motion_detector.process_frame(nut_frame, "nut_cam")
                    if motion_detected:
                        self._log_motion_event("NutCam")
                
                frame_count += 1
                
                # Log status every 100 frames (~3 seconds at 30fps)
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    self.logger.debug(f"Processed {frame_count} frames, {fps:.1f} FPS avg")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(1)  # Wait before retrying
    
    def _log_motion_event(self, camera_name):
        """Log a motion detection event with statistics."""
        camera_id = "critter_cam" if camera_name == "CritterCam" else "nut_cam"
        stats = self.motion_detector.get_camera_stats(camera_id)
        
        self.logger.info(f"🔴 MOTION DETECTED in {camera_name}! "
                        f"Events: {stats['motion_events_count']}, "
                        f"Frames: {stats['frames_processed']}")
    
    def stop(self):
        """Stop the headless camera system."""
        self.logger.info("Stopping headless camera system...")
        self.running = False
        
        # Wait for monitor thread to finish
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        # Release camera resources
        if self.camera_manager:
            self.camera_manager.release()
        
        # Log final statistics
        if self.motion_detector:
            for camera_id in ["critter_cam", "nut_cam"]:
                stats = self.motion_detector.get_camera_stats(camera_id)
                if stats['frames_processed'] > 0:
                    self.logger.info(f"Final stats for {camera_id}: "
                                   f"{stats['frames_processed']} frames, "
                                   f"{stats['motion_events_count']} motion events")
        
        self.logger.info("Headless camera system stopped")
    
    def get_status(self):
        """Get current system status (for web dashboard integration)."""
        camera_info = self.camera_manager.get_camera_info() if self.camera_manager else {}
        
        status = {
            'running': self.running,
            'app_name': self.app_config,
            'cameras': camera_info,
            'motion_detection': {
                'active': self.motion_detector is not None
            }
        }
        
        if self.motion_detector:
            # Add motion statistics
            for camera_id in ["critter_cam", "nut_cam"]:
                stats = self.motion_detector.get_camera_stats(camera_id)
                status['motion_detection'][camera_id] = stats
        
        return status


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger = get_logger("headless")
    logger.info(f"Received signal {signum}, shutting down...")
    if 'nutflix_app' in globals():
        nutflix_app.stop()
    sys.exit(0)


def main():
    """Main function for headless operation."""
    global nutflix_app
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    logger = get_logger("headless")
    logger.info("Starting Nutflix Lite in headless mode...")
    
    try:
        # Initialize and start the headless system
        nutflix_app = NutflixHeadless()
        
        if not nutflix_app.start():
            logger.error("Failed to start headless system")
            sys.exit(1)
        
        logger.info("Nutflix Lite headless system started successfully!")
        logger.info("Press Ctrl+C to stop")
        
        # Keep the main thread alive
        while nutflix_app.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if 'nutflix_app' in locals():
            nutflix_app.stop()


if __name__ == "__main__":
    main()
