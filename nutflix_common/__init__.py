"""
Nutflix Common Package
Shared utilities and modules for Nutflix and Nutflix Lite projects
"""

__version__ = "0.1.0"
__author__ = "Nutflix Team"

# Make key modules easily importable
from .config_loader import load_config
from .motion_utils import MotionDetector, MotionConfig, create_motion_detector
from .logger import get_logger, get_motion_logger, get_camera_logger, get_ai_logger

__all__ = [
    'load_config', 
    'MotionDetector', 
    'MotionConfig', 
    'create_motion_detector',
    'get_logger',
    'get_motion_logger',
    'get_camera_logger', 
    'get_ai_logger'
]
