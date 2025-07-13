#!/usr/bin/env python3
"""
Release script for Runchat Blender Addon
Builds the package and generates the repository index in one command.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode == 0

def main():
    # Get the script directory and project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print("🚀 Runchat Blender Addon Release Builder")
    print("=" * 50)
    
    # Change to project root
    os.chdir(project_root)
    
    # Step 1: Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Step 2: Build the package
    print("\n📦 Building addon package...")
    if not run_command("python build.py --no-install"):
        print("❌ Build failed!")
        sys.exit(1)
    
    # Step 3: Generate repository index
    print("\n📋 Generating repository index...")
    if not run_command("python scripts/generate-repository.py dist"):
        print("❌ Repository index generation failed!")
        print("Make sure Blender is installed and available in PATH")
        sys.exit(1)
    
    # Step 4: Show results
    print("\n✅ Release build completed successfully!")
    print("=" * 50)
    
    # Find the built package
    dist_files = list(Path("dist").glob("*.zip"))
    if dist_files:
        package_path = dist_files[0]
        package_size = package_path.stat().st_size / (1024 * 1024)  # MB
        print(f"📦 Package: {package_path}")
        print(f"📏 Size: {package_size:.1f} MB")
    
    # Check for index.json
    index_path = Path("dist/index.json")
    if index_path.exists():
        print(f"📋 Repository index: {index_path}")
        print("🌐 Repository URL: https://github.com/jpazzi/runchat-blender/raw/main/dist/index.json")
    
    print("\n🎉 Ready to release!")
    print("Next steps:")
    print("1. Test the package locally")
    print("2. Commit and push the changes:")
    print("   git add dist/")
    
    # Extract version from package name for commit message
    if dist_files:
        package_name = dist_files[0].stem  # e.g., "runchat-blender-v1.2.0"
        version = package_name.split('-')[-1]  # e.g., "v1.2.0"
        print(f"   git commit -m 'Release {version}'")
    else:
        print("   git commit -m 'Release build'")
    
    print("   git push origin main")
    print("3. Create a GitHub release and upload the .zip file")

if __name__ == "__main__":
    main() 