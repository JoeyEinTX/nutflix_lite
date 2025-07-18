#!/usr/bin/env python3
"""
Logging utilities for Nutflix Common
Provides standardized logging across all Nutflix projects
"""

import logging
import sys
import os
from typing import Optional, Dict
from datetime import datetime

# Global registry to track configured loggers (singleton pattern)
_configured_loggers: Dict[str, logging.Logger] = {}
_root_handler_configured = False


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Get a standardized logger instance with consistent formatting.
    
    Uses singleton pattern to ensure loggers are not reconfigured multiple times.
    
    Args:
        name: Logger name (e.g., "motion", "camera", "ai", "server")
        level: Log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = get_logger("motion")
        >>> logger.info("Motion detected in camera 1")
        [2025-07-18 10:30:45] [INFO] [motion] - Motion detected in camera 1
    """
    global _configured_loggers, _root_handler_configured
    
    # Return existing logger if already configured
    if name in _configured_loggers:
        return _configured_loggers[name]
    
    # Create new logger
    logger = logging.getLogger(f"nutflix.{name}")
    
    # Convert string level to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Configure root handler only once
    if not _root_handler_configured:
        _configure_root_handler()
        _root_handler_configured = True
    
    # Store in registry
    _configured_loggers[name] = logger
    
    return logger


def _configure_root_handler():
    """Configure the root logging handler with standard formatting."""
    # Get the root nutflix logger
    root_logger = logging.getLogger("nutflix")
    
    # Remove any existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatter with standardized format
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    # Prevent propagation to avoid duplicate messages
    root_logger.propagate = False


def set_global_log_level(level: str) -> None:
    """
    Set the log level for all nutflix loggers.
    
    Args:
        level: Log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Update root logger
    root_logger = logging.getLogger("nutflix")
    root_logger.setLevel(log_level)
    
    # Update all registered loggers
    for logger in _configured_loggers.values():
        logger.setLevel(log_level)


def add_file_handler(log_file_path: str, level: str = "INFO") -> None:
    """
    Add file logging to all nutflix loggers.
    
    Args:
        log_file_path: Path to log file
        level: Log level for file handler
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger("nutflix")
    
    # Create file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Use same formatter as console
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Add to root logger
    root_logger.addHandler(file_handler)


def configure_from_config(config: dict) -> None:
    """
    Configure logging from a configuration dictionary.
    
    Args:
        config: Configuration dictionary with logging settings
        
    Example config:
        {
            "logging": {
                "level": "INFO",
                "file": "/var/log/nutflix/app.log",
                "file_level": "DEBUG"
            }
        }
    """
    logging_config = config.get('logging', {})
    
    # Set global log level
    if 'level' in logging_config:
        set_global_log_level(logging_config['level'])
    
    # Add file handler if specified
    if 'file' in logging_config:
        file_level = logging_config.get('file_level', 'INFO')
        add_file_handler(logging_config['file'], file_level)


def get_logger_stats() -> Dict[str, any]:
    """
    Get statistics about configured loggers.
    
    Returns:
        Dictionary with logger statistics
    """
    return {
        'configured_loggers_count': len(_configured_loggers),
        'logger_names': list(_configured_loggers.keys()),
        'root_handler_configured': _root_handler_configured,
        'root_logger_level': logging.getLogger("nutflix").level,
        'root_logger_handlers_count': len(logging.getLogger("nutflix").handlers)
    }


# Convenience loggers for common subsystems
def get_motion_logger() -> logging.Logger:
    """Get logger for motion detection subsystem."""
    return get_logger("motion")


def get_camera_logger() -> logging.Logger:
    """Get logger for camera subsystem."""
    return get_logger("camera")


def get_ai_logger() -> logging.Logger:
    """Get logger for AI/ML subsystem."""
    return get_logger("ai")


def get_server_logger() -> logging.Logger:
    """Get logger for server subsystem."""
    return get_logger("server")


def get_config_logger() -> logging.Logger:
    """Get logger for configuration subsystem."""
    return get_logger("config")


# Initialize default logger on import (for backwards compatibility)
_default_logger = None


def get_default_logger() -> logging.Logger:
    """Get the default nutflix logger."""
    global _default_logger
    if _default_logger is None:
        _default_logger = get_logger("app")
    return _default_logger


# Example usage and testing
if __name__ == "__main__":
    print("Testing Nutflix Logger...")
    print("=" * 50)
    
    # Test basic logging
    logger = get_logger("test")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test different subsystem loggers
    motion_logger = get_motion_logger()
    motion_logger.info("Motion detected in camera 1")
    
    camera_logger = get_camera_logger()
    camera_logger.info("Camera initialized successfully")
    
    ai_logger = get_ai_logger()
    ai_logger.info("AI model loaded")
    
    # Test singleton behavior
    logger2 = get_logger("test")
    print(f"Same logger instance: {logger is logger2}")
    
    # Test log level changes
    print("\nChanging log level to DEBUG...")
    set_global_log_level("DEBUG")
    logger.debug("This debug message should now appear")
    
    # Test file logging (to temporary file)
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        temp_log_path = f.name
    
    add_file_handler(temp_log_path)
    logger.info("This message should appear in both console and file")
    
    # Read back from file
    with open(temp_log_path, 'r') as f:
        file_content = f.read()
        print(f"\nFile content:\n{file_content}")
    
    # Clean up
    os.unlink(temp_log_path)
    
    # Show statistics
    stats = get_logger_stats()
    print(f"\nLogger statistics: {stats}")
    
    print("\n" + "=" * 50)
    print("✅ Logger testing completed!")
