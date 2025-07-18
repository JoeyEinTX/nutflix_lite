#!/usr/bin/env python3
"""
Demo: Nutflix Common Logger in Action
Shows how the standardized logging works across different subsystems
"""

import sys
sys.path.insert(0, 'nutflix_common')

from logger import (
    get_logger, 
    get_motion_logger, 
    get_camera_logger, 
    get_ai_logger,
    set_global_log_level,
    get_logger_stats
)

def demo_nutflix_logging():
    """Demonstrate the nutflix_common logging system."""
    print("🎬 Nutflix Common Logger Demo")
    print("=" * 50)
    
    # Create loggers for different subsystems
    app_logger = get_logger("app")
    motion_logger = get_motion_logger()
    camera_logger = get_camera_logger()
    ai_logger = get_ai_logger()
    server_logger = get_logger("server")
    
    print("\n📋 Simulating application startup...")
    app_logger.info("Nutflix Lite application starting")
    app_logger.info("Loading configuration...")
    
    print("\n📷 Initializing camera system...")
    camera_logger.info("Camera manager initialized")
    camera_logger.info("CritterCam detected and ready")
    camera_logger.info("NutCam detected and ready")
    
    print("\n🔍 Setting up motion detection...")
    motion_logger.info("Motion detection system initialized")
    motion_logger.info("Background subtraction models ready")
    
    print("\n🧠 Loading AI components...")
    ai_logger.info("AI models loaded successfully")
    ai_logger.info("Object detection ready")
    
    print("\n⚠️  Simulating some warnings and errors...")
    camera_logger.warning("Camera 1 frame rate slightly low")
    motion_logger.error("Motion detection failed for frame 1234")
    server_logger.warning("High memory usage detected")
    
    print("\n🔧 Changing log level to DEBUG...")
    set_global_log_level("DEBUG")
    
    motion_logger.debug("Processing frame with background subtraction")
    ai_logger.debug("Running object detection on frame")
    camera_logger.debug("Frame capture successful")
    
    print("\n📊 Logger Statistics:")
    stats = get_logger_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed! The nutflix_common logger provides:")
    print("  🎯 Standardized formatting across all modules")
    print("  🔄 Singleton pattern for consistent logging")
    print("  🏷️  Subsystem-specific loggers (motion, camera, ai, etc.)")
    print("  ⚙️  Configurable log levels")
    print("  📈 Statistics and monitoring")
    print("  🚀 Ready for production use!")

if __name__ == "__main__":
    demo_nutflix_logging()
