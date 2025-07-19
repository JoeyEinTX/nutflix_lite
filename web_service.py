#!/usr/bin/env python3
"""
Nutflix Web Service
Standalone web dashboard service that integrates with the camera system.
This service runs independently and communicates with the main camera system.
"""

import sys
import os
import time
import signal
import threading
from typing import Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nutflix_common.config_loader import load_config
from nutflix_common.logger import get_logger, configure_from_config
from camera_manager import CameraManager
from web.dashboard.app import run_web_server, set_camera_manager

class NutflixWebService:
    """Web service that provides dashboard interface with camera feeds."""
    
    def __init__(self, config_path="config.yaml"):
        """Initialize the web service."""
        self.logger = get_logger("web_service")
        self.running = False
        self.camera_manager: Optional[CameraManager] = None
        self.web_thread: Optional[threading.Thread] = None
        
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
        self.camera_config = self.config.get('cameras', {})
        
        self.logger.info("Nutflix Web Service initialized")
    
    def _camera_status_callback(self, camera_name: str, status: str):
        """Handle camera status updates."""
        self.logger.info(f"Camera status update: {camera_name} = {status}")
        # The web app will handle status updates through the existing REST API
        # This callback is just for logging
    
    def _get_default_config(self):
        """Get default configuration if config file loading fails."""
        return {
            'cameras': {
                'critter_cam_id': 0,
                'nut_cam_id': 1
            }
        }
    
    def start(self):
        """Start the web service."""
        if self.running:
            self.logger.warning("Web service already running")
            return
        
        self.logger.info("Starting Nutflix Web Service...")
        self.running = True
        
        try:
            # Initialize camera manager for video feeds
            self.logger.info("Initializing camera manager for video feeds...")
            self.camera_manager = CameraManager(
                config=self.config,
                status_callback=self._camera_status_callback
            )
            
            # Check if cameras are available
            self.logger.info("Checking camera availability...")
            critter_available = self.camera_manager.is_camera_available('critter_cam')
            nut_available = self.camera_manager.is_camera_available('nut_cam')
            
            self.logger.info(f"Camera status - Critter: {'Available' if critter_available else 'Unavailable'}")
            self.logger.info(f"Camera status - Nut: {'Available' if nut_available else 'Unavailable'}")
            
            if not (critter_available or nut_available):
                self.logger.warning("No cameras are available - web service will serve placeholder feeds")
            else:
                self.logger.info("Camera manager initialized successfully")
            
            # Set camera manager in web app
            set_camera_manager(self.camera_manager)
            self.logger.info("Camera manager connected to web dashboard")
            
            # Start web server
            self.logger.info("Starting web dashboard server...")
            self._start_web_server()
            
        except Exception as e:
            self.logger.error(f"Failed to start web service: {e}")
            self.stop()
            raise
    
    def _start_web_server(self):
        """Start the web server in the main thread."""
        try:
            # Add a small delay to ensure camera manager is fully initialized
            time.sleep(2)
            
            # Run web server on main thread (required for SocketIO)
            run_web_server(
                app_context=self,
                host='0.0.0.0',
                port=5000,
                debug=False
            )
        except Exception as e:
            self.logger.error(f"Web server error: {e}")
            raise
    
    def stop(self):
        """Stop the web service."""
        if not self.running:
            return
        
        self.logger.info("Stopping Nutflix Web Service...")
        self.running = False
        
        # Clean up camera manager
        if self.camera_manager:
            try:
                self.camera_manager.cleanup()
                self.logger.info("Camera manager cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up camera manager: {e}")
        
        self.logger.info("Web service stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

def main():
    """Main entry point for the web service."""
    service = NutflixWebService()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, service._signal_handler)
    signal.signal(signal.SIGTERM, service._signal_handler)
    
    try:
        service.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Service error: {e}")
    finally:
        service.stop()

if __name__ == "__main__":
    main()
