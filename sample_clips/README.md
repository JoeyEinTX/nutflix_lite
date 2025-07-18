# Sample Video Clips - DEPRECATED

⚠️ **This directory is no longer used in the production version of Nutflix Lite.**

The application now runs exclusively with real hardware cameras on Raspberry Pi.

## Migration Notes

If you need to test the application without hardware cameras, consider:

1. **Use a webcam**: Connect a USB webcam and update camera IDs in `config.yaml`
2. **Use virtual cameras**: Set up OBS Virtual Camera or similar software
3. **Test with single camera**: Modify the code to work with just one camera

## Hardware Setup

For production deployment on Raspberry Pi:
- Connect your cameras to USB ports or CSI camera connectors
- Update `config.yaml` with correct camera IDs (usually 0 and 1)
- Ensure adequate power supply for multiple cameras
