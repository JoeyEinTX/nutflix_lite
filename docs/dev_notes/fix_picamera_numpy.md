# 📸 Nutflix Project: Camera + NumPy Compatibility Fix

## 🧠 Problem Summary

We encountered a ValueError during import of picamera2, specifically:

```
ValueError: numpy.dtype size changed, may indicate binary incompatibility.
Expected 96 from C header, got 88 from PyObject
```

This was caused by a binary mismatch between numpy, simplejpeg, and other C-extension dependencies used by picamera2.

## 🔍 Root Cause

- Conflicting versions of numpy were installed: system-level vs virtual environment
- opencv-python requires numpy <2.3.0, but we had mistakenly installed 2.3.1
- simplejpeg (used by picamera2) is a compiled extension that broke when numpy's ABI changed

## 🛠️ Fix Procedure

All commands were executed inside the project virtual environment (.venv).

```bash
# 1. Uninstall conflicting system packages (if previously installed)
sudo apt remove --purge python3-numpy python3-picamera2 python3-simplejpeg

# 2. Deactivate any broken numpy from the venv
pip uninstall -y numpy

# 3. Install the correct numpy version
pip install --no-cache-dir numpy==2.2.0

# 4. Reinstall Picamera2 (which depends on simplejpeg, av, etc.)
pip install --no-cache-dir picamera2
```

## ✅ Success

- `from picamera2 import Picamera2` now works without error
- Live MJPEG feeds appear correctly in the Nutflix dashboard
- No ABI errors, full Picamera2 functionality restored

## 📌 Dev Notes

**requirements.txt pinned versions:**
```
numpy==2.2.0
picamera2==0.3.27
opencv-python<4.13
simplejpeg==1.8.2
```

**Tips:**
- Use `--no-cache-dir` to force clean installs
- Avoid mixing system-level Python packages with virtual environments
- Don't auto-upgrade numpy or opencv-python without testing ABI compatibility

## 🎯 Related Files Modified

- `camera_manager.py` - Refactored to use Picamera2 exclusively
- `web_service.py` - Port changed from 5000 to 5050 to avoid conflicts
- `requirements.txt` - Version pinning for compatibility

## 🚀 Testing Verification

After the fix, the following should work without errors:

```python
# Test 1: Import verification
from picamera2 import Picamera2
import numpy as np
import cv2

# Test 2: Camera initialization
camera = Picamera2(camera_num=0)
config = camera.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
camera.configure(config)
camera.start()

# Test 3: Frame capture
frame = camera.capture_array()
assert frame.shape == (480, 640, 3)
camera.stop()
camera.close()
```

## 🔧 Troubleshooting

If you encounter similar issues in the future:

1. **Check numpy version compatibility:**
   ```bash
   pip list | grep numpy
   python -c "import numpy; print(numpy.__version__)"
   ```

2. **Verify no system package conflicts:**
   ```bash
   dpkg -l | grep python3-numpy
   dpkg -l | grep python3-picamera2
   ```

3. **Clean reinstall if needed:**
   ```bash
   pip uninstall -y numpy opencv-python picamera2 simplejpeg
   pip install --no-cache-dir numpy==2.2.0 opencv-python<4.13 picamera2
   ```

---

*Document created: 2025-07-19*  
*Last updated: 2025-07-19*  
*Status: ✅ Resolved*
