#!/usr/bin/env python3
"""
Status Manager for Nutflix Lite
Handles communication between the main camera system and web dashboard.
"""

import requests
import json
from typing import Dict, Any
from nutflix_common.logger import get_logger

logger = get_logger("status")

class StatusManager:
    """Manages status updates between camera system and web dashboard."""
    
    def __init__(self, dashboard_url: str = "http://localhost:5000"):
        """
        Initialize status manager.
        
        Args:
            dashboard_url: URL of the web dashboard
        """
        self.dashboard_url = dashboard_url
        self.status = {
            'cameras': {
                'critter_cam': 'Initializing...',
                'nut_cam': 'Initializing...'
            },
            'motion_detection': 'ready',
            'system': 'active'
        }
        logger.info(f"StatusManager initialized for dashboard at {dashboard_url}")
    
    def update_camera_status(self, camera_name: str, status: str):
        """
        Update camera status and notify dashboard.
        
        Args:
            camera_name: Either 'critter_cam' or 'nut_cam'
            status: New status ('Ready', 'Error', 'Initializing...', etc.)
        """
        if camera_name in self.status['cameras']:
            self.status['cameras'][camera_name] = status
            logger.info(f"{camera_name} status updated to: {status}")
            
            # Try to notify dashboard via HTTP POST
            self._notify_dashboard()
        else:
            logger.warning(f"Unknown camera name: {camera_name}")
    
    def update_motion_status(self, status: str):
        """Update motion detection status."""
        self.status['motion_detection'] = status
        logger.info(f"Motion detection status: {status}")
        self._notify_dashboard()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status dictionary."""
        return self.status.copy()
    
    def _notify_dashboard(self):
        """Send status update to dashboard via HTTP."""
        try:
            # Send POST request to dashboard status endpoint
            response = requests.post(
                f"{self.dashboard_url}/api/status", 
                json=self.status,
                timeout=2
            )
            if response.status_code == 200:
                logger.debug("Dashboard status updated successfully")
            else:
                logger.warning(f"Dashboard update failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.debug(f"Could not reach dashboard: {e}")
        except Exception as e:
            logger.error(f"Error notifying dashboard: {e}")

# Global status manager instance
status_manager = None

def get_status_manager() -> StatusManager:
    """Get the global status manager instance."""
    global status_manager
    if status_manager is None:
        status_manager = StatusManager()
    return status_manager

def update_camera_status(camera_name: str, status: str):
    """Convenience function to update camera status."""
    get_status_manager().update_camera_status(camera_name, status)
