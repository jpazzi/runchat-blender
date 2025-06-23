#!/usr/bin/env python3
"""
runchat Blender Addon - Simple Installer
Installs the refactored addon to Blender's addons directory
"""

import os
import sys
import shutil
import platform
from pathlib import Path

def get_blender_addons_path():
    """Get the Blender addons directory path"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        base_path = Path.home() / "Library/Application Support/Blender"
    elif system == "Linux":
        base_path = Path.home() / ".config/blender"
    elif system == "Windows":
        base_path = Path(os.environ["APPDATA"]) / "Blender Foundation/Blender"
    else:
        raise Exception(f"Unsupported operating system: {system}")
    
    # Find the latest Blender version
    if not base_path.exists():
        raise Exception(f"Blender directory not found: {base_path}")
    
    versions = [d for d in base_path.iterdir() if d.is_dir() and d.name.replace('.', '').isdigit()]
    if not versions:
        raise Exception(f"No Blender versions found in {base_path}")
    
    # Sort versions and get the latest
    latest_version = sorted(versions, key=lambda x: [int(i) for i in x.name.split('.')])[-1]
    addons_path = latest_version / "scripts/addons"
    
    return addons_path

def install_addon():
    """Install the runchat addon"""
    print("🚀 runchat Blender Addon Installer")
    print("=" * 40)
    
    # Get current directory (should be the addon directory)
    addon_source = Path(__file__).parent
    addon_name = "runchat-blender"
    
    print(f"📁 Source: {addon_source}")
    
    try:
        # Get Blender addons path
        addons_path = get_blender_addons_path()
        print(f"🎯 Target: {addons_path}")
        
        # Create addons directory if it doesn't exist
        addons_path.mkdir(parents=True, exist_ok=True)
        
        # Install path
        install_path = addons_path / addon_name
        
        # Remove existing installation
        if install_path.exists():
            print(f"🗑️ Removing existing installation...")
            shutil.rmtree(install_path)
        
        # Copy addon files
        print(f"📦 Installing addon...")
        shutil.copytree(addon_source, install_path, 
                       ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.git*', '*.zip'))
        
        print(f"✅ Successfully installed to: {install_path}")
        print()
        print("🎉 Installation Complete!")
        print()
        print("📋 Next Steps:")
        print("1. Open Blender")
        print("2. Go to Edit → Preferences → Add-ons")
        print("3. Search for 'runchat'")
        print("4. Enable the addon")
        print("5. Set your API key in addon preferences")
        print()
        print("🎯 The addon will appear in Properties → Scene Properties → runchat")
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        print()
        print("💡 Alternative: Use Blender's built-in addon installer:")
        print("1. Create a zip of this folder")
        print("2. In Blender: Edit → Preferences → Add-ons → Install...")
        print("3. Select the zip file")
        sys.exit(1)

if __name__ == "__main__":
    install_addon() 