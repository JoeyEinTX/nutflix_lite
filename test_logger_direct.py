#!/usr/bin/env python3
"""
Direct test for logger module (without OpenCV dependencies)
"""

def test_logger_directly():
    """Test logger module directly without importing motion_utils."""
    print("Testing logger module directly...")
    
    # Import logger directly to avoid OpenCV dependency
    import sys
    sys.path.insert(0, 'nutflix_common')
    from logger import get_logger, get_motion_logger, set_global_log_level, get_logger_stats
    
    print("✅ Logger imported successfully")
    
    # Test basic functionality
    app_logger = get_logger("app")
    app_logger.info("Application started")
    
    motion_logger = get_motion_logger()
    motion_logger.info("Motion system ready")
    
    # Test singleton
    app_logger2 = get_logger("app")
    print(f"Singleton test: {app_logger is app_logger2}")
    
    # Test stats
    stats = get_logger_stats()
    print(f"Logger stats: {stats}")
    
    print("✅ Direct logger test completed successfully!")

if __name__ == "__main__":
    test_logger_directly()
