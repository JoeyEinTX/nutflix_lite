#!/usr/bin/env python3
"""
Config Loader Module for Nutflix Common
Handles loading and parsing configuration files (YAML, JSON)
"""

import yaml
import json
import os
import logging
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML or JSON file.
    
    Args:
        config_path: Path to the configuration file (.yaml, .yml, or .json)
        
    Returns:
        Dictionary containing the parsed configuration
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        ValueError: If the file format is not supported or invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Determine file type from extension
    _, ext = os.path.splitext(config_path.lower())
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            if ext in ['.yaml', '.yml']:
                config = yaml.safe_load(file)
                logger.info(f"Successfully loaded YAML config from: {config_path}")
            elif ext == '.json':
                config = json.load(file)
                logger.info(f"Successfully loaded JSON config from: {config_path}")
            else:
                raise ValueError(f"Unsupported config file format: {ext}. Supported: .yaml, .yml, .json")
        
        # Ensure we return a dictionary
        if not isinstance(config, dict):
            raise ValueError(f"Config file must contain a dictionary/object, got: {type(config)}")
            
        return config
        
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format in {config_path}: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {config_path}: {e}")
    except Exception as e:
        raise ValueError(f"Error loading config from {config_path}: {e}")


def load_config_with_defaults(config_path: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load configuration with default values fallback.
    
    Args:
        config_path: Path to the configuration file
        defaults: Default configuration values
        
    Returns:
        Merged configuration (file values override defaults)
    """
    try:
        config = load_config(config_path)
        # Merge defaults with loaded config (config overrides defaults)
        merged_config = {**defaults, **config}
        logger.info(f"Config loaded with defaults applied from: {config_path}")
        return merged_config
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}, using defaults only")
        return defaults.copy()
    except Exception as e:
        logger.error(f"Error loading config: {e}, using defaults only")
        return defaults.copy()


def save_config(config: Dict[str, Any], config_path: str, format_type: str = 'yaml') -> None:
    """
    Save configuration to a file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path where to save the configuration
        format_type: Output format ('yaml' or 'json')
    """
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as file:
            if format_type.lower() == 'yaml':
                yaml.dump(config, file, default_flow_style=False, indent=2)
            elif format_type.lower() == 'json':
                json.dump(config, file, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported format: {format_type}. Use 'yaml' or 'json'")
        
        logger.info(f"Configuration saved to: {config_path}")
        
    except Exception as e:
        logger.error(f"Error saving config to {config_path}: {e}")
        raise


def validate_config(config: Dict[str, Any], required_keys: list) -> bool:
    """
    Validate that required keys exist in the configuration.
    
    Args:
        config: Configuration dictionary to validate
        required_keys: List of required key names
        
    Returns:
        True if all required keys exist, False otherwise
    """
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        logger.error(f"Missing required configuration keys: {missing_keys}")
        return False
    
    logger.info("Configuration validation passed")
    return True


# Example usage and testing
if __name__ == "__main__":
    # Test the config loader
    test_config = {
        'app_name': 'Nutflix Lite',
        'cameras': {
            'critter_cam_id': 0,
            'nut_cam_id': 1,
            'debug_mode': True
        },
        'motion_detection': {
            'threshold': 500,
            'sensitivity': 25,
            'cooldown': 2.0
        }
    }
    
    print("Testing config_loader module...")
    
    # Save a test config
    test_path = "test_config.yaml"
    save_config(test_config, test_path)
    
    # Load it back
    loaded_config = load_config(test_path)
    print(f"Loaded config: {loaded_config}")
    
    # Test validation
    required_keys = ['app_name', 'cameras', 'motion_detection']
    is_valid = validate_config(loaded_config, required_keys)
    print(f"Config is valid: {is_valid}")
    
    # Clean up test file
    if os.path.exists(test_path):
        os.remove(test_path)
    
    print("Config loader test completed!")
