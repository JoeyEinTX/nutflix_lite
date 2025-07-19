#!/usr/bin/env python3
"""
Test script for libcamera bridge on Raspberry Pi
"""

import sys
import time
from camera_manager import CameraManager
from nutflix_common.config_loader import load_config
from nutflix_common.logger import get_logger

logger = get_logger("test_libcamera")

def test_cameras():
    """Test camera functionality with libcamera bridge."""
    logger.info("Testing libcamera bridge...")
    
    try:
        # Load configuration
        config = load_config("config.yaml")
        camera_config = config['cameras']
        
        logger.info(f"Camera config: {camera_config}")
        
        # Initialize camera manager
        camera_manager = CameraManager(camera_config)
        
        logger.info("Camera manager initialized, testing frame capture...")
        
        # Test reading frames
        for i in range(10):
            logger.info(f"Reading frame set {i+1}/10...")
            frames = camera_manager.read_frames()
            
            critter_frame = frames.get('critter_cam')
            nut_frame = frames.get('nut_cam')
            
            if critter_frame is not None:
                logger.info(f"CritterCam frame: {critter_frame.shape}")
            else:
                logger.warning("CritterCam frame is None")
            
            if nut_frame is not None:
                logger.info(f"NutCam frame: {nut_frame.shape}")
            else:
                logger.warning("NutCam frame is None")
            
            time.sleep(1)
        
        logger.info("Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    finally:
        # Clean up
        try:
            camera_manager.cleanup()
        except:
            pass

if __name__ == "__main__":
    success = test_cameras()
    sys.exit(0 if success else 1)
