#!/usr/bin/env python3
"""
Installation script for RunChat Blender Addon
Run this script to automatically install the addon to your Blender addons directory
"""

import os
import sys
import subprocess
import shutil
import zipfile
import tempfile
from pathlib import Path

def get_blender_addons_path():
    """Get the Blender addons directory path"""
    
    # Common Blender addon paths
    if sys.platform == "win32":
        # Windows
        blender_paths = [
            Path.home() / "AppData/Roaming/Blender Foundation/Blender",
            Path("C:/Program Files/Blender Foundation/Blender")
        ]
    elif sys.platform == "darwin":
        # macOS
        blender_paths = [
            Path.home() / "Library/Application Support/Blender",
            Path("/Applications/Blender.app/Contents/Resources")
        ]
    else:
        # Linux
        blender_paths = [
            Path.home() / ".config/blender",
            Path("/usr/share/blender")
        ]
    
    # Find existing Blender installation
    for base_path in blender_paths:
        if base_path.exists():
            # Look for version directories
            for version_dir in base_path.glob("*"):
                if version_dir.is_dir() and version_dir.name.replace(".", "").isdigit():
                    addons_path = version_dir / "scripts/addons"
                    if addons_path.exists():
                        return addons_path
    
    return None

def install_addon(source_dir, target_dir, addon_name="runchat_blender"):
    """Install the addon to the target directory"""
    
    target_addon_dir = target_dir / addon_name
    
    # Remove existing installation
    if target_addon_dir.exists():
        print(f"Removing existing installation at {target_addon_dir}")
        shutil.rmtree(target_addon_dir)
    
    # Copy addon files
    print(f"Installing addon to {target_addon_dir}")
    shutil.copytree(source_dir, target_addon_dir)
    
    return target_addon_dir

def create_addon_zip(addon_name="runchat_blender"):
    """Create a zip file of the addon for manual installation with correct structure"""
    
    # Get current directory (where this script is located)
    script_dir = Path(__file__).parent.absolute()
    
    # Verify this is the addon directory
    required_files = ["__init__.py", "runchat_nodes.py", "preferences.py", "utils.py"]
    missing_files = [f for f in required_files if not (script_dir / f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Make sure you're running this script from the addon directory")
        return None
    
    output_path = f"{addon_name}.zip"
    
    print(f"📦 Creating addon zip: {output_path}")
    print(f"📁 Source directory: {script_dir}")
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(script_dir):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                # Skip hidden files, compiled Python files, and this install script
                if (file.startswith('.') or 
                    file.endswith('.pyc') or 
                    file == 'install.py' or
                    file.endswith('.zip')):
                    continue
                
                file_path = Path(root) / file
                
                # Create the correct archive path: addon_name/relative_path
                relative_path = file_path.relative_to(script_dir)
                archive_path = f"{addon_name}/{relative_path}"
                
                print(f"   Adding: {relative_path}")
                zipf.write(file_path, archive_path)
    
    print(f"✅ Addon zip created: {output_path}")
    return output_path

def check_pil_availability():
    """Check if PIL/Pillow is available"""
    try:
        import PIL
        print("✅ PIL/Pillow is available")
        return True
    except ImportError:
        print("⚠️ PIL/Pillow not available - image compression will be limited")
        return False

def install_pil():
    """Attempt to install PIL/Pillow"""
    try:
        print("📦 Installing PIL/Pillow...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "Pillow"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PIL/Pillow installed successfully!")
            return True
        else:
            print(f"❌ PIL/Pillow installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing PIL/Pillow: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 RunChat Blender Addon Installation")
    print("=" * 50)
    
    # Check arguments
    skip_deps = "--no-deps" in sys.argv
    
    # Check dependencies
    if not skip_deps:
        print("🔍 Checking dependencies...")
        
        # Check PIL availability
        pil_available = check_pil_availability()
        if not pil_available:
            response = input("📥 Install PIL/Pillow for enhanced image compression? (y/n): ").lower()
            if response in ['y', 'yes']:
                install_pil()
    
    # Create addon package
    print("\n📦 Creating addon package...")
    addon_zip = create_addon_zip()
    
    if addon_zip:
        print(f"✅ Addon package created: {addon_zip}")
        print("\n📋 Installation Instructions:")
        print(f"1. Open Blender")
        print(f"2. Go to Edit > Preferences > Add-ons")
        print(f"3. Click 'Install...' and select: {addon_zip}")
        print(f"4. Enable 'RunChat Blender Nodes'")
        print(f"5. Configure your API key in the addon preferences")
        
        if not skip_deps and not check_pil_availability():
            print(f"\n⚠️ Note: PIL/Pillow not available")
            print(f"   Image compression will be limited")
            print(f"   You can install it later from the addon preferences")
        
    else:
        print("❌ Failed to create addon package")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 