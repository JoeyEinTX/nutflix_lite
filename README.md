# Nutflix Lite

A lightweight dual-camera GUI application with motion detection capabilities, built using Python and OpenCV. This project demonstrates modular package architecture with reusable components.

## Features

- **Dual Camera Interface**: View feeds from two cameras simultaneously
- **Motion Detection**: OpenCV-based motion detection with configurable sensitivity
- **Debug Mode**: Use sample video files when hardware cameras aren't available
- **Modular Architecture**: Reusable components via the `nutflix_common` package
- **Centralized Logging**: Standardized logging across all application components
- **Configuration Management**: YAML-based configuration with validation

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install nutflix_common package
   ```

2. **Run the Application**:
   ```bash
   python main_with_motion_utils.py
   ```

3. **Debug Mode** (without hardware cameras):
   - Place sample videos in `sample_clips/` directory
   - Set `debug_mode: true` in your configuration

## Project Structure

```
nutflix_lite/
├── nutflix_common/          # Reusable package for Nutflix projects
│   ├── __init__.py         # Package exports
│   ├── config_loader.py    # YAML/JSON configuration management
│   ├── motion_utils.py     # Motion detection utilities
│   └── logger.py           # Standardized logging system
├── camera_manager.py       # Production camera management
├── main_with_motion_utils.py # Main GUI application
├── sample_clips/           # Sample videos for debug mode
├── setup.py               # Package installation
└── requirements.txt       # Dependencies
```

## Nutflix Common Package

The `nutflix_common` package provides reusable utilities for all Nutflix projects:

### Configuration Management
```python
from nutflix_common.config_loader import load_config
config = load_config('config.yaml')
```

### Motion Detection
```python
from nutflix_common.motion_utils import MotionDetector
detector = MotionDetector()
motion_detected = detector.process_frame(frame)
```

### Logging
```python
from nutflix_common.logger import get_logger
logger = get_logger("my_app")
logger.info("Application started")
```

## Configuration

Create a `config.yaml` file with your settings:

```yaml
cameras:
  debug_mode: false
  camera1_id: 0
  camera2_id: 1

motion_detection:
  enabled: true
  threshold: 1000
  min_area: 500

logging:
  level: INFO
  file_output: true
```

## Development

- **Testing**: Run `python -m pytest` for unit tests
- **Linting**: Use `flake8` for code quality
- **Type Checking**: Run `mypy` for type validation

## Dependencies

- Python 3.8+
- OpenCV 4.x
- tkinter (usually included with Python)
- PyYAML
- NumPy

## License

This project is open source and available under the MIT License. nutfliI just created main.py with a basic dual-camera GUI preview in tkinter. Let’s start enhancing it. First, add OpenCV-based motion detection and log motion events in the scrolling log window.
