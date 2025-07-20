# Sample Video Clips

This directory contains sample video files for debugging and testing the Nutflix Lite application when hardware cameras are not available.

## Required Video Files

For dual-camera mode testing, place the following video files in this directory:

- `camera1.mp4` - Simulates first camera feed
- `camera2.mp4` - Simulates second camera feed

## Video Format Requirements

- **Format**: MP4 (H.264 codec recommended)
- **Resolution**: 640x480 or higher
- **Frame Rate**: 30 FPS recommended
- **Duration**: Any length (will loop automatically)

## Testing Motion Detection

For optimal motion detection testing:

1. Include videos with moving objects (people, vehicles, animals)
2. Have periods of stillness to test background subtraction
3. Use good lighting and contrast
4. Avoid excessive camera shake

## Debug Mode Usage

When running the application, set `debug_mode: true` in your configuration file to use these sample videos instead of hardware cameras.

Example config:
```yaml
cameras:
  debug_mode: true
  camera1_id: 0  # Will use camera1.mp4
  camera2_id: 1  # Will use camera2.mp4
```

## Sample Video Sources

Free sample videos can be downloaded from:
- [Pixabay](https://pixabay.com/videos/)
- [Pexels](https://www.pexels.com/videos/)
- [Videvo](https://www.videvo.net/)

Remember to respect licensing terms when using sample videos.
