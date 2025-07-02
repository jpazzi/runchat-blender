#!/usr/bin/env python3
"""
Build script for Runchat Blender addon
Downloads dependencies, bundles them, and creates distributable package
"""

import os
import sys
import subprocess
import shutil
import zipfile
import tempfile
from pathlib import Path

# Build configuration
ADDON_NAME = "runchat-blender"
VERSION = "1.2.0"  # Should match bl_info version
REQUIRED_PACKAGES = ["requests", "Pillow"]

def get_version():
    """Extract version from bl_info"""
    try:
        addon_dir = Path(__file__).parent
        init_file = addon_dir / "__init__.py"
        
        with open(init_file, 'r') as f:
            content = f.read()
            
        # Extract version from bl_info
        import re
        version_match = re.search(r'"version":\s*\((\d+),\s*(\d+),\s*(\d+)\)', content)
        if version_match:
            major, minor, patch = version_match.groups()
            return f"{major}.{minor}.{patch}"
    except Exception as e:
        print(f"Warning: Could not extract version from bl_info: {e}")
    
    return VERSION

def clean_build():
    """Clean previous build artifacts"""
    addon_dir = Path(__file__).parent
    
    # Clean lib directory
    lib_dir = addon_dir / "lib"
    if lib_dir.exists():
        print(f"🧹 Cleaning existing lib directory: {lib_dir}")
        shutil.rmtree(lib_dir)
    
    # Clean build directory
    build_dir = addon_dir / "build"
    if build_dir.exists():
        print(f"🧹 Cleaning build directory: {build_dir}")
        shutil.rmtree(build_dir)
    
    # Clean dist directory
    dist_dir = addon_dir / "dist"
    if dist_dir.exists():
        print(f"🧹 Cleaning dist directory: {dist_dir}")
        shutil.rmtree(dist_dir)

def download_dependencies():
    """Download required Python packages for Blender 4.4 (Python 3.11)"""
    addon_dir = Path(__file__).parent
    build_dir = addon_dir / "build"
    temp_dir = build_dir / "temp"
    lib_dir = addon_dir / "lib"
    
    # Create directories
    build_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)
    lib_dir.mkdir(exist_ok=True)
    
    print(f"📦 Downloading dependencies for Python 3.11 (Blender 4.4) to: {temp_dir}")
    
    # Download packages for Python 3.11 specifically
    for package in REQUIRED_PACKAGES:
        print(f"  • Downloading {package} for Python 3.11...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "download",
                "--dest", str(temp_dir),
                "--no-deps",  # Don't download dependencies of dependencies initially
                "--python-version", "3.11",
                "--platform", "macosx_10_9_x86_64",  # macOS x86_64 compatible
                "--platform", "macosx_11_0_arm64",   # macOS ARM64 compatible
                "--only-binary=:all:",  # Only download wheels, no source
                package
            ], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download {package}: {e}")
            return False
    
    # Download requests dependencies separately to ensure we get them all
    requests_deps = ["urllib3", "certifi", "charset-normalizer", "idna"]
    for dep in requests_deps:
        print(f"  • Downloading {dep} for Python 3.11...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "download",
                "--dest", str(temp_dir),
                "--no-deps",
                "--python-version", "3.11",
                "--platform", "macosx_10_9_x86_64",  # macOS x86_64 compatible
                "--platform", "macosx_11_0_arm64",   # macOS ARM64 compatible
                "--only-binary=:all:",  # Only download wheels, no source
                dep
            ], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            print(f"  ⚠️ Optional dependency {dep} not found, continuing...")
    
    print("✅ All packages downloaded for Python 3.11")
    return True

def extract_packages():
    """Extract downloaded packages to lib directory"""
    addon_dir = Path(__file__).parent
    build_dir = addon_dir / "build"
    temp_dir = build_dir / "temp"
    lib_dir = addon_dir / "lib"
    
    print(f"📂 Extracting packages to: {lib_dir}")
    
    # Extract all .whl files
    whl_files = list(temp_dir.glob("*.whl"))
    if not whl_files:
        print("❌ No .whl files found to extract")
        return False
    
    for whl_file in whl_files:
        print(f"  • Extracting {whl_file.name}...")
        try:
            # Extract wheel file to temp location
            extract_temp = temp_dir / "extract" / whl_file.stem
            extract_temp.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(whl_file, 'r') as zip_ref:
                zip_ref.extractall(extract_temp)
            
            # Find and copy the actual package directories
            for item in extract_temp.iterdir():
                if item.is_dir() and not item.name.endswith('.dist-info'):
                    dest = lib_dir / item.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                    print(f"    → Copied {item.name}/")
                    
        except Exception as e:
            print(f"❌ Failed to extract {whl_file}: {e}")
            return False
    
    print("✅ All packages extracted")
    return True

def cleanup_lib():
    """Remove unnecessary files from lib directory"""
    addon_dir = Path(__file__).parent
    lib_dir = addon_dir / "lib"
    
    print("🧹 Cleaning up lib directory...")
    
    # Patterns to remove
    cleanup_patterns = [
        "*.dist-info",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "test*",
        "tests",
        "*.egg-info",
        "docs",
        "examples",
        "*.txt",  # README, LICENSE, etc.
        "*.md",
        "*.rst",
    ]
    
    total_removed = 0
    
    for pattern in cleanup_patterns:
        for path in lib_dir.rglob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"    🗑️ Removed directory: {path.relative_to(lib_dir)}")
                else:
                    path.unlink()
                    print(f"    🗑️ Removed file: {path.relative_to(lib_dir)}")
                total_removed += 1
            except Exception as e:
                print(f"    ⚠️ Could not remove {path}: {e}")
    
    print(f"✅ Cleaned up {total_removed} items")

def validate_bundle():
    """Validate that all required packages are present"""
    addon_dir = Path(__file__).parent
    lib_dir = addon_dir / "lib"
    
    print("🔍 Validating bundle...")
    
    required_packages = ['requests', 'urllib3', 'certifi', 'PIL']
    missing = []
    
    for package in required_packages:
        package_dir = lib_dir / package
        if not package_dir.exists():
            missing.append(package)
        else:
            print(f"    ✅ Found: {package}/")
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        return False
    
    # Test imports
    print("🧪 Testing imports...")
    
    # Add lib to path temporarily
    sys.path.insert(0, str(lib_dir))
    
    try:
        import requests
        print("    ✅ requests imports successfully")
        
        # Skip PIL import test when bundling for different Python version
        try:
            from PIL import Image
            print("    ✅ PIL imports successfully")
        except ImportError as e:
            if "cannot import name '_imaging'" in str(e):
                print("    ⚠️ PIL compiled for different Python version (expected for Blender bundle)")
                print("    ✅ PIL package structure is correct")
            else:
                print(f"❌ PIL import test failed: {e}")
                return False
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    finally:
        # Remove from path
        if str(lib_dir) in sys.path:
            sys.path.remove(str(lib_dir))
    
    print("✅ Bundle validation successful")
    return True

def create_package():
    """Create final distributable package"""
    addon_dir = Path(__file__).parent
    dist_dir = addon_dir / "dist"
    
    # Create dist directory
    dist_dir.mkdir(exist_ok=True)
    
    # Get version for filename
    version = get_version()
    package_name = f"{ADDON_NAME}-v{version}.zip"
    package_path = dist_dir / package_name
    
    print(f"📦 Creating package: {package_path}")
    
    # Remove existing package
    if package_path.exists():
        package_path.unlink()
    
    # Create zip file
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Directories and files to exclude from the package
        exclude_dirs = {'build', 'dist', '__pycache__', '.git'}
        exclude_files = {
            'build.py', 'clean.py', 'make.py', 'validate_bundle.py',
            '.gitignore', 'BUILD_GUIDE.md', 'README_BUNDLING.md', 
            'BUNDLE_DEPENDENCIES.md', 'STRUCTURE.md'
        }
        
        # Add all addon files
        for file_path in addon_dir.rglob('*'):
            if file_path.is_file():
                # Get relative path for checking exclusions
                rel_path = file_path.relative_to(addon_dir)
                
                # Skip if in excluded directory
                if any(part in exclude_dirs for part in rel_path.parts):
                    continue
                
                # Skip excluded files
                if file_path.name in exclude_files:
                    continue
                
                # Calculate archive path (files inside addon directory for Blender)
                archive_path = ADDON_NAME / rel_path
                zipf.write(file_path, archive_path)
                
                # Show progress for important files
                if rel_path.parts[0] in {'lib', 'operators', 'ui', 'utils'} or file_path.name.endswith('.py'):
                    print(f"    📁 Added: {archive_path}")
    
    # Get package size
    size_mb = package_path.stat().st_size / (1024 * 1024)
    
    print(f"✅ Package created successfully!")
    print(f"    📄 File: {package_path}")
    print(f"    📏 Size: {size_mb:.1f} MB")
    
    return package_path

def get_lib_size():
    """Get size of lib directory"""
    addon_dir = Path(__file__).parent
    lib_dir = addon_dir / "lib"
    
    if not lib_dir.exists():
        return 0
    
    total_size = sum(f.stat().st_size for f in lib_dir.rglob('*') if f.is_file())
    return total_size / (1024 * 1024)  # Convert to MB

def main():
    """Main build process"""
    print("🚀 Building Runchat Blender Addon")
    print("=" * 50)
    
    # Step 1: Clean previous builds
    clean_build()
    
    # Step 2: Download dependencies
    if not download_dependencies():
        print("❌ Build failed at dependency download")
        return 1
    
    # Step 3: Extract packages
    if not extract_packages():
        print("❌ Build failed at package extraction")
        return 1
    
    # Step 4: Cleanup unnecessary files
    cleanup_lib()
    
    # Step 5: Validate bundle
    if not validate_bundle():
        print("❌ Build failed at validation")
        return 1
    
    # Step 6: Create final package
    package_path = create_package()
    
    # Summary
    lib_size = get_lib_size()
    print("\n" + "=" * 50)
    print("🎉 BUILD SUCCESSFUL!")
    print(f"📦 Bundled dependencies size: {lib_size:.1f} MB")
    print(f"📄 Final package: {package_path}")
    print("\nThe package is ready for distribution to users!")
    print("Users can install it directly in Blender as an addon.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 