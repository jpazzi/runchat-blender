#!/usr/bin/env python3
"""
Clean script for Runchat Blender addon
Removes build artifacts and bundled dependencies
"""

import shutil
import sys
from pathlib import Path

def clean_all():
    """Remove all build artifacts and bundled dependencies"""
    addon_dir = Path(__file__).parent
    
    print("🧹 Cleaning Runchat Blender addon build artifacts...")
    
    # Items to clean
    items_to_clean = [
        addon_dir / "lib",              # Bundled dependencies
        addon_dir / "build",            # Build directory
        addon_dir / "dist",             # Distribution directory
    ]
    
    # Add __pycache__ directories
    pycache_dirs = list(addon_dir.rglob("__pycache__"))
    items_to_clean.extend(pycache_dirs)
    
    # Add .pyc files
    pyc_files = list(addon_dir.rglob("*.pyc"))
    items_to_clean.extend(pyc_files)
    
    cleaned_count = 0
    
    for item in items_to_clean:
        if item.exists():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"🗑️  Removed directory: {item.relative_to(addon_dir)}")
                else:
                    item.unlink()
                    print(f"🗑️  Removed file: {item.relative_to(addon_dir)}")
                cleaned_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {item}: {e}")
    
    if cleaned_count == 0:
        print("✨ Already clean - no artifacts found")
    else:
        print(f"✅ Cleaned {cleaned_count} items")
    
    print("\nProject is now clean and ready for a fresh build.")

if __name__ == "__main__":
    clean_all() 