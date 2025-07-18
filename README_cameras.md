# Nutflix Lite Camera System

## Overview
The `CameraManager` class provides a production-ready dual-camera system for Nutflix Lite that works on Raspberry Pi hardware.

## Features

### 🎥 Dual Camera Support
- **CritterCam**: Primary camera (default ID: 0)
- **NutCam**: Secondary camera (default ID: 1)

### 🔧 Production Mode
- Uses real hardware cameras via `cv2.VideoCapture(camera_id)`
- Raises `RuntimeError` if cameras can't be opened
- Perfect for Raspberry Pi deployment

## Usage

### Basic Usage
```python
from camera_manager import CameraManager

# Configuration
config = {
    'critter_cam_id': 0,
    'nut_cam_id': 1
}

# Initialize camera manager
camera_manager = CameraManager(config)

# Read frames from both cameras
frames = camera_manager.read_frames()
critter_frame = frames['critter_cam']  # OpenCV frame or None
nut_frame = frames['nut_cam']          # OpenCV frame or None

# Clean up
camera_manager.release()
```

### Context Manager (Recommended)
```python
with CameraManager(config) as cam_manager:
    frames = cam_manager.read_frames()
    # Process frames...
    # Automatic cleanup on exit
```

### Integration with Existing GUI
See `integration_example.py` for complete integration examples with your existing `main.py`.

## File Structure
```
nutflix_lite/
├── main.py                    # Main GUI application
├── camera_manager.py          # Camera management class
├── integration_example.py     # Integration examples
└── README_cameras.md         # This file
```

## API Reference

### CameraManager Class

#### Constructor
```python
CameraManager(config: Dict[str, Any])
```
- `config['critter_cam_id']`: Camera ID for CritterCam (default: 0)
- `config['nut_cam_id']`: Camera ID for NutCam (default: 1)

#### Methods
- `read_frames()` → `Dict[str, Optional[frame]]`: Read one frame from each camera
- `release()`: Release all camera resources
- `is_camera_available(camera_name)` → `bool`: Check if specific camera is available
- `get_camera_info()` → `Dict`: Get camera configuration and status

## Error Handling
- Comprehensive logging for all operations
- Graceful fallback when cameras are unavailable
- Clear error messages for debugging
- Production-ready exception handling

## Deployment Notes

### For Raspberry Pi
```python
config = {
    'debug_mode': False,
    'critter_cam_id': 0,
    'nut_cam_id': 1
}
```

Make sure your camera hardware is properly connected and the camera IDs match your system configuration.
