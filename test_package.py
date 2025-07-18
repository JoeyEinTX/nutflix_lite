#!/usr/bin/env python3
"""
Simple test script for nutflix_common package
"""

def test_import():
    try:
        import nutflix_common
        print("✅ nutflix_common package imported successfully!")
        print(f"Package version: {nutflix_common.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import nutflix_common: {e}")
        return False

def test_config_loader():
    try:
        from nutflix_common.config_loader import load_config
        print("✅ config_loader module imported successfully!")
        
        # Test loading the config.yaml file
        config = load_config('config.yaml')
        print(f"✅ Config loaded successfully!")
        print(f"App name: {config.get('app_name')}")
        print(f"Camera IDs: {config['cameras']['critter_cam_id']}, {config['cameras']['nut_cam_id']}")
        print(f"Motion threshold: {config['motion_detection']['threshold']}")
        return True
    except Exception as e:
        print(f"❌ Failed to test config_loader: {e}")
        return False

if __name__ == "__main__":
    print("Testing nutflix_common package...")
    print("=" * 50)
    
    # Test 1: Import package
    import_success = test_import()
    
    if import_success:
        # Test 2: Test config loader
        config_success = test_config_loader()
        
        if config_success:
            print("=" * 50)
            print("🎉 All tests passed! nutflix_common package is working correctly.")
        else:
            print("=" * 50)
            print("⚠️  Package imports but config_loader has issues.")
    else:
        print("=" * 50)
        print("❌ Package import failed.")
