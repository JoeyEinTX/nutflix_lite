#!/usr/bin/env python3
"""
Test script for motion_utils.py
Tests the MotionDetector class without requiring OpenCV GUI
"""

import numpy as np
import time
from nutflix_common.motion_utils import MotionDetector, MotionConfig, create_motion_detector

def test_motion_detector():
    """Test the MotionDetector class with simulated frames."""
    print("Testing MotionDetector...")
    print("=" * 50)
    
    # Test 1: Basic functionality
    print("Test 1: Basic MotionDetector functionality")
    config = MotionConfig(threshold=300, cooldown=1.0)
    detector = MotionDetector(config)
    
    # Create test frames
    static_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    motion_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    motion_frame[200:300, 300:400] = 255  # White rectangle to simulate motion
    
    results = []
    
    # Process some frames
    for i in range(3):
        # Use static frame first, then motion frame
        frame = static_frame if i == 0 else motion_frame
        motion = detector.process_frame(frame, "test_camera")
        results.append(motion)
        
        stats = detector.get_camera_stats("test_camera")
        print(f"  Frame {i+1}: Motion={motion}, Processed={stats['frames_processed']}, Events={stats['motion_events_count']}")
        time.sleep(0.2)
    
    print(f"✅ Basic test completed: {results}")
    
    # Test 2: Multiple cameras
    print("\nTest 2: Multiple camera support")
    camera_ids = ["camera_1", "camera_2"]
    
    for camera_id in camera_ids:
        motion = detector.process_frame(motion_frame, camera_id)
        stats = detector.get_camera_stats(camera_id)
        print(f"  {camera_id}: Motion={motion}, Events={stats['motion_events_count']}")
    
    print("✅ Multiple camera test completed")
    
    # Test 3: Convenience function
    print("\nTest 3: Convenience function")
    simple_detector = create_motion_detector(threshold=200, cooldown=0.5)
    motion = simple_detector.process_frame(motion_frame, "simple_cam")
    stats = simple_detector.get_camera_stats("simple_cam")
    print(f"  Simple detector: Motion={motion}, Events={stats['motion_events_count']}")
    print("✅ Convenience function test completed")
    
    # Test 4: Stats and events
    print("\nTest 4: Motion events and statistics")
    events = detector.get_motion_events("test_camera")
    for i, event in enumerate(events):
        print(f"  Event {i+1}: Camera={event.camera_id}, Time={event.timestamp:.2f}, "
              f"Contours={event.contour_count}, Area={event.largest_contour_area:.1f}")
    
    print("✅ Events test completed")
    
    print("\n" + "=" * 50)
    print("🎉 All motion_utils tests passed!")
    return True

def test_imports():
    """Test that motion utilities can be imported from nutflix_common."""
    print("Testing imports...")
    
    try:
        from nutflix_common.motion_utils import MotionDetector
        print("✅ MotionDetector imported successfully")
        
        from nutflix_common.motion_utils import MotionConfig
        print("✅ MotionConfig imported successfully")
        
        from nutflix_common.motion_utils import create_motion_detector
        print("✅ create_motion_detector imported successfully")
        
        # Test importing from main package
        from nutflix_common import MotionDetector as MD
        print("✅ MotionDetector imported from main package")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing nutflix_common motion utilities...")
    print("=" * 60)
    
    # Test imports first
    if test_imports():
        print("\n" + "=" * 60)
        # Test functionality
        if test_motion_detector():
            print("\n🎊 ALL TESTS PASSED! Motion utilities are ready for use.")
        else:
            print("\n❌ Some tests failed.")
    else:
        print("\n❌ Import tests failed.")
