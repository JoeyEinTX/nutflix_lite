#!/usr/bin/env python3
"""
Test script for the Nutflix web dashboard
"""

import sys
import os
import time
import requests
import threading

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.dashboard.app import run_web_server_threaded

def test_web_dashboard():
    """Test the web dashboard functionality."""
    print("🧪 Testing Nutflix Web Dashboard...")
    
    # Start the web server in a thread
    print("🚀 Starting web server...")
    server_thread = run_web_server_threaded(host='localhost', port=5001)  # Use different port for testing
    
    # Give the server time to start
    time.sleep(2)
    
    try:
        # Test the main page
        print("📡 Testing main dashboard page...")
        response = requests.get("http://localhost:5001/", timeout=5)
        if response.status_code == 200:
            print("✅ Main page accessible")
            if "Welcome to Nutflix" in response.text:
                print("✅ Content loaded correctly")
            else:
                print("⚠️  Content may not be loading properly")
        else:
            print(f"❌ Main page failed: {response.status_code}")
        
        # Test health check
        print("🏥 Testing health check endpoint...")
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('status')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Test API status
        print("📊 Testing API status endpoint...")
        response = requests.get("http://localhost:5001/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API status: {data.get('dashboard')}")
        else:
            print(f"❌ API status failed: {response.status_code}")
        
        print("🎉 Web dashboard test completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to web server - it may not have started properly")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print("\n📝 To access the dashboard manually:")
    print("   1. Run: python web/dashboard/app.py")
    print("   2. Open: http://localhost:5000")
    print("   3. Check the WebSocket connection status")

if __name__ == "__main__":
    test_web_dashboard()
