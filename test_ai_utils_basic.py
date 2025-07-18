#!/usr/bin/env python3
"""
Simple test for AI utilities without OpenCV dependency at test level.

This script tests the ai_utils module by importing it directly and checking
the module structure without actually running OpenCV-dependent code.
"""

import sys
import os
import py_compile

# Add the parent directory to the path so we can import nutflix_common
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_module_imports():
    """Test that the ai_utils module can be imported and has expected attributes."""
    print("Testing AI utils module imports...")
    
    try:
        # Test individual module import
        from nutflix_common import ai_utils
        print("✅ nutflix_common.ai_utils imported successfully")
        
        # Check for expected classes and functions
        expected_items = ['ImageClassifier', 'load_model', 'classify_frame', 'DEMO_LABELS']
        
        for item in expected_items:
            if hasattr(ai_utils, item):
                print(f"✅ Found {item}")
            else:
                print(f"❌ Missing {item}")
                return False
                
        # Test package-level imports
        from nutflix_common import ImageClassifier, load_model, classify_frame
        print("✅ Package-level imports working")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_syntax_validation():
    """Test that the ai_utils.py file has valid Python syntax."""
    print("\nTesting Python syntax validation...")
    
    ai_utils_path = "/workspaces/nutflix_lite/nutflix_common/ai_utils.py"
    
    try:
        py_compile.compile(ai_utils_path, doraise=True)
        print("✅ ai_utils.py syntax is valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error in ai_utils.py: {e}")
        return False

def test_demo_classifier_instantiation():
    """Test that we can create a demo classifier without ML dependencies."""
    print("\nTesting demo classifier instantiation...")
    
    try:
        from nutflix_common.ai_utils import ImageClassifier
        
        # Create demo classifier
        classifier = ImageClassifier(model_type="demo")
        print("✅ Demo ImageClassifier created")
        
        # Check that it has the expected methods
        expected_methods = ['load_model', 'classify_frame']
        for method in expected_methods:
            if hasattr(classifier, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Demo classifier instantiation failed: {e}")
        return False

def test_logger_integration():
    """Test that the AI utils properly integrate with the logging system."""
    print("\nTesting logger integration...")
    
    try:
        from nutflix_common.logger import get_logger
        
        # Test getting AI logger
        ai_logger = get_logger("ai")
        print("✅ AI logger obtained successfully")
        
        # Test that logger has expected methods
        expected_methods = ['info', 'warning', 'error', 'debug']
        for method in expected_methods:
            if hasattr(ai_logger, method):
                print(f"✅ Logger method {method} exists")
            else:
                print(f"❌ Logger method {method} missing")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Logger integration test failed: {e}")
        return False

def main():
    """Run all non-OpenCV tests."""
    print("Starting AI utilities basic tests (no OpenCV execution)...")
    
    tests = [
        ("Module Imports", test_module_imports),
        ("Syntax Validation", test_syntax_validation),
        ("Demo Classifier Instantiation", test_demo_classifier_instantiation),
        ("Logger Integration", test_logger_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- Running {test_name} Test ---")
        try:
            success = test_func()
            if success:
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
            
    print(f"\n--- Test Summary ---")
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        print("\nNote: To test full functionality including frame classification,")
        print("run this in an environment with display support:")
        print("python -c 'from nutflix_common.ai_utils import main; main()'")
        return True
    else:
        print(f"💥 {total - passed} tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
