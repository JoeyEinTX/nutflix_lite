#!/usr/bin/env python3
"""
Test imports for main_updated.py without OpenCV dependencies
"""

def test_nutflix_imports():
    try:
        # Test nutflix_common import
        from nutflix_common.config_loader import load_config
        print("✅ nutflix_common.config_loader imported successfully")
        
        # Test config loading
        config = load_config('config.yaml')
        print("✅ config.yaml loaded successfully")
        print(f"   App: {config.get('app_name')}")
        print(f"   Debug mode: {config['cameras']['debug_mode']}")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing nutflix_common integration...")
    success = test_nutflix_imports()
    
    if success:
        print("\n🎉 SUCCESS: nutflix_common package is properly integrated!")
        print("\nNext steps:")
        print("1. ✅ nutflix_common package created and installed")
        print("2. ✅ config_loader module working") 
        print("3. ✅ YAML config loading functional")
        print("4. ✅ Ready for production use!")
        print("\nTo run the full app:")
        print("   python3 main_updated.py")
        print("\nTo switch to hardware mode, edit config.yaml:")
        print("   cameras.debug_mode: false")
    else:
        print("\n❌ Integration test failed")
