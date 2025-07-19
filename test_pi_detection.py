#!/usr/bin/env python3
"""
Quick test for Raspberry Pi detection
"""

import platform
import os

def test_pi_detection():
    print("=== Raspberry Pi Detection Test ===")
    
    # Check /proc/cpuinfo
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read().lower()
            print(f"cpuinfo contains 'raspberry pi': {'raspberry pi' in cpuinfo}")
            print(f"cpuinfo contains 'bcm': {'bcm' in cpuinfo}")
            print("First few lines of cpuinfo:")
            lines = cpuinfo.split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"  {line}")
    except Exception as e:
        print(f"Error reading cpuinfo: {e}")
    
    # Check /proc/device-tree/model
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().lower()
            print(f"device-tree model: {model}")
            print(f"model contains 'raspberry pi': {'raspberry pi' in model}")
    except Exception as e:
        print(f"Error reading device-tree model: {e}")
    
    # Check platform
    machine = platform.machine().lower()
    print(f"platform.machine(): {machine}")
    print(f"machine contains 'arm': {'arm' in machine}")
    print(f"machine contains 'aarch64': {'aarch64' in machine}")
    
    # Check Pi-specific paths
    print(f"/opt/vc exists: {os.path.exists('/opt/vc')}")
    print(f"/usr/bin/libcamera-hello exists: {os.path.exists('/usr/bin/libcamera-hello')}")
    
    # Final determination
    is_pi = False
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read().lower()
            if 'raspberry pi' in cpuinfo or 'bcm' in cpuinfo:
                is_pi = True
        
        if not is_pi:
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    model = f.read().lower()
                    if 'raspberry pi' in model:
                        is_pi = True
            except:
                pass
        
        if not is_pi and ('arm' in machine or 'aarch64' in machine):
            if os.path.exists('/opt/vc') or os.path.exists('/usr/bin/libcamera-hello'):
                is_pi = True
    except:
        pass
    
    print(f"\n=== RESULT: Is Raspberry Pi? {is_pi} ===")
    return is_pi

if __name__ == "__main__":
    test_pi_detection()
