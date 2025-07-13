#!/usr/bin/env python3
"""
Generate repository index.json using Blender's official server-generate command.
This follows the official Blender static repository guidelines.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def find_blender_executable():
    """Find Blender executable on different platforms."""
    # Common Blender locations
    possible_paths = [
        "/Applications/Blender.app/Contents/MacOS/Blender",  # macOS
        "/usr/bin/blender",  # Linux
        "/usr/local/bin/blender",  # Linux (alternative)
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",  # Windows
        "C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe",  # Windows (x86)
    ]
    
    # Check if blender is in PATH
    if shutil.which("blender"):
        return "blender"
    
    # Check common installation paths
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def generate_repository_index(repo_dir):
    """Generate index.json using Blender's official command, then update URLs for GitHub hosting."""
    blender_exe = find_blender_executable()
    
    if not blender_exe:
        print("❌ Blender executable not found!")
        print("Please install Blender or add it to your PATH")
        print("Common locations:")
        print("  macOS: /Applications/Blender.app/Contents/MacOS/Blender")
        print("  Linux: /usr/bin/blender")
        print("  Windows: C:\\Program Files\\Blender Foundation\\Blender\\blender.exe")
        return False
    
    # Ensure repo directory exists
    repo_path = Path(repo_dir)
    if not repo_path.exists():
        print(f"❌ Repository directory not found: {repo_path}")
        return False
    
    # Check if there are any .zip files
    zip_files = list(repo_path.glob("*.zip"))
    if not zip_files:
        print(f"❌ No .zip files found in {repo_path}")
        return False
    
    print(f"📦 Found {len(zip_files)} package(s):")
    for zip_file in zip_files:
        print(f"   - {zip_file.name}")
    
    # Run Blender's server-generate command
    try:
        cmd = [blender_exe, "--command", "extension", "server-generate", f"--repo-dir={repo_path}"]
        print(f"🔄 Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            index_file = repo_path / "index.json"
            if index_file.exists():
                print(f"✅ Successfully generated {index_file}")
                print(f"   File size: {index_file.stat().st_size} bytes")
                
                # Update URLs for GitHub hosting
                update_github_urls(index_file)
                
                return True
            else:
                print("❌ Command succeeded but index.json was not created")
                return False
        else:
            print(f"❌ Command failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def update_github_urls(index_file):
    """Update the generated index.json to use GitHub raw URLs for downloads."""
    import json
    
    try:
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        # Update archive_url for each extension to use GitHub raw URL
        for extension in data.get('data', []):
            if 'archive_url' in extension:
                # Convert relative path to GitHub raw URL
                filename = extension['archive_url'].lstrip('./')
                github_raw_url = f"https://github.com/jpazzi/runchat-blender/raw/main/dist/{filename}"
                extension['archive_url'] = github_raw_url
                print(f"🔗 Updated download URL: {github_raw_url}")
        
        # Write back the updated JSON
        with open(index_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Updated index.json with GitHub raw URLs")
        
    except Exception as e:
        print(f"❌ Error updating GitHub URLs: {e}")

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python generate-repository.py <repo-directory>")
        print("Example: python generate-repository.py ./dist")
        sys.exit(1)
    
    repo_dir = sys.argv[1]
    
    if generate_repository_index(repo_dir):
        print(f"")
        print(f"📋 Next steps:")
        print(f"   1. Commit the generated index.json and package files")
        print(f"   2. Push to GitHub repository")
        print(f"   3. Users can add: https://github.com/jpazzi/runchat-blender/raw/main/dist/index.json")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 