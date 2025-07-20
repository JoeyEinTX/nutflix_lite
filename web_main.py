#!/usr/bin/env python3
"""
Nutflix Lite Web Dashboard Main Entry Point
This is the main entry point for the Nutflix Lite dashboard.
"""

import sys
import os

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(__file__))

# Import the Flask app and camera manager
from web.dashboard.app import app, set_camera_manager
from camera_manager import CameraManager

# Use nutflix_common logger
from nutflix_common.logger import get_logger

# Get logger for main service
logger = get_logger("web_main")

def main():
    """Main entry point for the Nutflix Lite web dashboard."""
    logger.info("Starting Nutflix Lite Web Dashboard")
    
    # Hardware config for Raspberry Pi dual cameras
    hardware_config = {
        'critter_cam_id': 0,  # CSI Camera 0
        'nut_cam_id': 1       # CSI Camera 1
    }
    
    try:
        # Initialize CameraManager
        logger.info("Initializing camera manager...")
        camera_manager = CameraManager(hardware_config)
        
        # Set the camera manager in the Flask app
        logger.info("Setting camera manager in Flask app...")
        set_camera_manager(camera_manager)
        
        # Attach camera_manager to app for additional access if needed
        app.camera_manager = camera_manager
        
        logger.info("Camera manager successfully initialized and attached to Flask app")
        
        # Start the Flask web server
        logger.info("Starting Flask web server on 0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5050, debug=True)
        
    except Exception as e:
        logger.error(f"Failed to start Nutflix Lite Web Dashboard: {e}")
        raise

if __name__ == '__main__':
    main()
