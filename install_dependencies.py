#!/usr/bin/env python3
"""
Script to download and bundle dependencies for Blender add-on
Run this script to prepare the dependencies before packaging the add-on
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """Download and bundle dependencies into the lib folder"""
    script_dir = Path(__file__).parent
    lib_dir = script_dir / "lib"
    
    # Create lib directory
    lib_dir.mkdir(exist_ok=True)
    
    # Required packages
    packages = [
        "requests",
        "Pillow",
    ]
    
    print("Downloading dependencies...")
    
    # Download packages using pip
    for package in packages:
        print(f"Downloading {package}...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--target", str(lib_dir),
            "--no-deps",  # Don't install dependencies of dependencies
            package
        ], check=True)
    
    # Clean up unnecessary files
    cleanup_patterns = [
        "*.dist-info",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "tests",
        "test",
    ]
    
    print("Cleaning up unnecessary files...")
    for pattern in cleanup_patterns:
        for path in lib_dir.rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    
    print("Dependencies installed successfully!")
    print(f"Total size: {get_directory_size(lib_dir)} MB")

def get_directory_size(path):
    """Get directory size in MB"""
    total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    return round(total / (1024 * 1024), 2)

if __name__ == "__main__":
    install_dependencies() 