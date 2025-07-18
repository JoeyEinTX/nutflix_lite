#!/usr/bin/env python3
"""
Test script for AI utilities module.

This script tests the ai_utils module without requiring ML dependencies
by using the demo classifier mode.
"""

import sys
import os
import numpy as np
import cv2

# Add the parent directory to the path so we can import nutflix_common
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from nutflix_common.ai_utils import load_model, classify_frame, ImageClassifier
    from nutflix_common.logger import get_logger
    
    logger = get_logger("ai_test")
    
    def test_demo_classifier():
        """Test the demo classifier functionality."""
        logger.info("Testing demo classifier...")
        
        # Create test frames with different characteristics
        test_frames = {
            "bright_blue": np.full((480, 640, 3), [255, 100, 100], dtype=np.uint8),  # Bright blue
            "dark_scene": np.full((480, 640, 3), [30, 30, 30], dtype=np.uint8),      # Dark
            "bright_white": np.full((480, 640, 3), [200, 200, 200], dtype=np.uint8), # Bright white
        }
        
        # Load demo model
        classifier = load_model("demo")
        
        if classifier is None:
            logger.error("Failed to load demo classifier")
            return False
            
        # Test classification on different frames
        results = {}
        for frame_name, frame in test_frames.items():
            label, confidence = classify_frame(classifier, frame)
            results[frame_name] = (label, confidence)
            logger.info(f"{frame_name}: {label} (confidence: {confidence:.3f})")
            
        # Verify reasonable results
        bright_label, bright_conf = results["bright_white"]
        dark_label, dark_conf = results["dark_scene"]
        blue_label, blue_conf = results["bright_blue"]
        
        # Basic sanity checks
        assert bright_conf > 0.5, f"Bright frame confidence too low: {bright_conf}"
        assert dark_conf > 0.5, f"Dark frame confidence too low: {dark_conf}"
        assert blue_conf > 0.5, f"Blue frame confidence too low: {blue_conf}"
        
        logger.info("Demo classifier tests passed!")
        return True
        
    def test_direct_instantiation():
        """Test direct instantiation of ImageClassifier."""
        logger.info("Testing direct ImageClassifier instantiation...")
        
        classifier = ImageClassifier(model_type="demo")
        success = classifier.load_model()
        
        if not success:
            logger.error("Failed to load model via direct instantiation")
            return False
            
        # Test with a simple frame
        test_frame = np.zeros((240, 320, 3), dtype=np.uint8)
        label, confidence = classifier.classify_frame(test_frame)
        
        logger.info(f"Direct instantiation result: {label} (confidence: {confidence:.3f})")
        
        assert confidence > 0.0, f"Confidence should be positive: {confidence}"
        assert isinstance(label, str), f"Label should be string: {type(label)}"
        
        logger.info("Direct instantiation tests passed!")
        return True
        
    def test_error_handling():
        """Test error handling scenarios."""
        logger.info("Testing error handling...")
        
        # Test with None model
        label, confidence = classify_frame(None, np.zeros((100, 100, 3), dtype=np.uint8))
        assert label == "error", f"Expected 'error' label, got: {label}"
        assert confidence == 0.0, f"Expected 0.0 confidence, got: {confidence}"
        
        # Test with invalid frame
        classifier = load_model("demo")
        try:
            # This might fail gracefully or succeed depending on OpenCV's handling
            label, confidence = classifier.classify_frame(np.array([1, 2, 3]))
            logger.info(f"Invalid frame handling: {label} (confidence: {confidence:.3f})")
        except Exception as e:
            logger.info(f"Invalid frame correctly raised exception: {e}")
            
        logger.info("Error handling tests completed!")
        return True
        
    def main():
        """Run all tests."""
        logger.info("Starting AI utilities tests...")
        
        tests = [
            ("Demo Classifier", test_demo_classifier),
            ("Direct Instantiation", test_direct_instantiation), 
            ("Error Handling", test_error_handling),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                logger.info(f"\n--- Running {test_name} Test ---")
                success = test_func()
                if success:
                    logger.info(f"✅ {test_name} test PASSED")
                    passed += 1
                else:
                    logger.error(f"❌ {test_name} test FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name} test FAILED with exception: {e}")
                
        logger.info(f"\n--- Test Summary ---")
        logger.info(f"Passed: {passed}/{total} tests")
        
        if passed == total:
            logger.info("🎉 All tests passed!")
            return True
        else:
            logger.error(f"💥 {total - passed} tests failed!")
            return False
            
    if __name__ == "__main__":
        success = main()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the nutflix_lite directory")
    print("and that nutflix_common is properly installed with: pip install -e .")
    sys.exit(1)
