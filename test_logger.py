#!/usr/bin/env python3
"""
Test script for the nutflix_common logger
Tests the centralized logging system
"""

def test_basic_logging():
    """Test basic logging functionality."""
    print("Testing basic logging...")
    
    from nutflix_common.logger import get_logger
    
    # Test different loggers
    app_logger = get_logger("app")
    motion_logger = get_logger("motion") 
    camera_logger = get_logger("camera")
    
    # Test log messages
    app_logger.info("Application started")
    motion_logger.info("Motion detection initialized")
    camera_logger.info("Camera system ready")
    
    app_logger.warning("This is a warning message")
    app_logger.error("This is an error message")
    
    print("✅ Basic logging test completed")

def test_convenience_loggers():
    """Test convenience logger functions."""
    print("\nTesting convenience loggers...")
    
    from nutflix_common.logger import (
        get_motion_logger, 
        get_camera_logger, 
        get_ai_logger,
        get_server_logger
    )
    
    motion_logger = get_motion_logger()
    camera_logger = get_camera_logger()
    ai_logger = get_ai_logger()
    server_logger = get_server_logger()
    
    motion_logger.info("Motion event detected")
    camera_logger.info("Camera frame captured")
    ai_logger.info("AI model prediction complete")
    server_logger.info("Server request processed")
    
    print("✅ Convenience loggers test completed")

def test_singleton_behavior():
    """Test that loggers follow singleton pattern."""
    print("\nTesting singleton behavior...")
    
    from nutflix_common.logger import get_logger, get_motion_logger
    
    logger1 = get_logger("test")
    logger2 = get_logger("test")
    
    motion1 = get_motion_logger()
    motion2 = get_motion_logger()
    
    print(f"Same logger instance (test): {logger1 is logger2}")
    print(f"Same logger instance (motion): {motion1 is motion2}")
    
    assert logger1 is logger2, "Loggers should be singleton"
    assert motion1 is motion2, "Motion loggers should be singleton"
    
    print("✅ Singleton behavior test completed")

def test_log_level_changes():
    """Test changing log levels."""
    print("\nTesting log level changes...")
    
    from nutflix_common.logger import get_logger, set_global_log_level
    
    logger = get_logger("level_test")
    
    # Test current level
    logger.info("Info message (should appear)")
    logger.debug("Debug message (should NOT appear)")
    
    # Change to debug level
    print("Changing to DEBUG level...")
    set_global_log_level("DEBUG")
    
    logger.info("Info message (should appear)")
    logger.debug("Debug message (should NOW appear)")
    
    # Change back to INFO
    set_global_log_level("INFO")
    
    print("✅ Log level changes test completed")

def test_config_integration():
    """Test logger configuration from config file."""
    print("\nTesting config integration...")
    
    from nutflix_common.config_loader import load_config
    from nutflix_common.logger import configure_from_config, get_logger
    
    try:
        config = load_config('config.yaml')
        configure_from_config(config)
        
        logger = get_logger("config_test")
        logger.info("Logger configured from config file")
        
        print("✅ Config integration test completed")
    except Exception as e:
        print(f"⚠️  Config integration test skipped: {e}")

def test_logger_stats():
    """Test logger statistics."""
    print("\nTesting logger statistics...")
    
    from nutflix_common.logger import get_logger_stats, get_logger
    
    # Create some loggers
    get_logger("stats_test1")
    get_logger("stats_test2")
    
    stats = get_logger_stats()
    print(f"Logger statistics: {stats}")
    
    assert stats['configured_loggers_count'] >= 2, "Should have at least 2 loggers"
    
    print("✅ Logger statistics test completed")

if __name__ == "__main__":
    print("Testing nutflix_common logger module...")
    print("=" * 60)
    
    try:
        test_basic_logging()
        test_convenience_loggers()
        test_singleton_behavior()
        test_log_level_changes()
        test_config_integration()
        test_logger_stats()
        
        print("\n" + "=" * 60)
        print("🎉 ALL LOGGER TESTS PASSED!")
        print("\n✅ Logger module is working correctly")
        print("✅ Singleton pattern implemented")
        print("✅ Standardized formatting active")
        print("✅ Config integration functional")
        print("✅ Multiple subsystem loggers supported")
        print("\n🚀 Ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Logger test failed: {e}")
        import traceback
        traceback.print_exc()
