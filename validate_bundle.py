#!/usr/bin/env python3
"""
Validation script for Runchat Blender addon bundled dependencies
Run this script to verify that all bundled dependencies are present and working
"""

import sys
import os
from pathlib import Path

def validate_bundle():
    """Validate that the addon has all required bundled dependencies"""
    
    # Get the addon directory
    addon_dir = Path(__file__).parent
    lib_dir = addon_dir / "lib"
    
    print("🔍 Validating Runchat Blender addon bundle...")
    print(f"📁 Addon directory: {addon_dir}")
    print(f"📦 Lib directory: {lib_dir}")
    
    # Check if lib directory exists
    if not lib_dir.exists():
        print("❌ CRITICAL: lib/ directory not found!")
        print("   The addon requires bundled dependencies in the lib/ folder.")
        print("   Please follow the bundling guide to create it.")
        return False
    
    # Add lib to path
    lib_str = str(lib_dir)
    if lib_str not in sys.path:
        sys.path.insert(0, lib_str)
    
    # Check for required package directories
    required_packages = ['requests', 'urllib3', 'certifi', 'charset_normalizer', 'PIL']
    missing_packages = []
    
    for package in required_packages:
        package_dir = lib_dir / package
        if not package_dir.exists():
            missing_packages.append(package)
        else:
            print(f"✅ Found: {package}/")
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Please complete the bundling process to include all dependencies.")
        return False
    
    # Test imports
    print("\n🧪 Testing imports...")
    
    try:
        import requests
        print("✅ requests imported successfully")
        
        # Test a simple request
        response = requests.get("https://httpbin.org/get", timeout=5)
        print(f"✅ HTTP test successful: {response.status_code}")
        
    except Exception as e:
        print(f"❌ requests test failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL imported successfully")
        
        # Test creating an image
        test_img = Image.new('RGB', (10, 10), color='red')
        print("✅ PIL test successful")
        
    except Exception as e:
        print(f"❌ PIL test failed: {e}")
        return False
    
    print("\n🎉 All bundled dependencies validated successfully!")
    print("   The addon is ready for distribution.")
    return True

if __name__ == "__main__":
    success = validate_bundle()
    sys.exit(0 if success else 1) 