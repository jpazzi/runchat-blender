#!/usr/bin/env python3
"""
Make script for Runchat Blender addon
Provides common build operations
"""

import sys
import subprocess
from pathlib import Path

def show_help():
    """Show available commands"""
    print("🚀 Runchat Blender Addon Build Tool")
    print("=" * 40)
    print("Commands:")
    print("  build     - Build addon with bundled dependencies")
    print("  clean     - Clean build artifacts")
    print("  validate  - Validate bundled dependencies")
    print("  help      - Show this help")
    print("\nUsage: python make.py <command>")

def run_build():
    """Run the build process"""
    addon_dir = Path(__file__).parent
    build_script = addon_dir / "build.py"
    
    print("🚀 Starting build process...")
    result = subprocess.run([sys.executable, str(build_script)])
    return result.returncode

def run_clean():
    """Run the clean process"""
    addon_dir = Path(__file__).parent
    clean_script = addon_dir / "clean.py"
    
    print("🧹 Starting clean process...")
    result = subprocess.run([sys.executable, str(clean_script)])
    return result.returncode

def run_validate():
    """Run the validation process"""
    addon_dir = Path(__file__).parent
    validate_script = addon_dir / "validate_bundle.py"
    
    if not validate_script.exists():
        print("❌ validate_bundle.py not found")
        return 1
    
    print("🔍 Starting validation process...")
    result = subprocess.run([sys.executable, str(validate_script)])
    return result.returncode

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_help()
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "build":
        return run_build()
    elif command == "clean":
        return run_clean()
    elif command == "validate":
        return run_validate()
    elif command in ["help", "-h", "--help"]:
        show_help()
        return 0
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 