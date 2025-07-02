# Runchat Blender Addon - Build Guide

This guide explains how to build the Runchat Blender addon with bundled dependencies for distribution.

## Project Structure

```
runchat-blender/                  # Self-contained addon directory
├── __init__.py                   # Addon entry point
├── api.py                        # API client
├── properties.py                 # Blender properties
├── operators/                    # Blender operators
├── ui/                           # UI panels
├── utils/                        # Utility modules
│   └── dependencies.py           # Dependency manager
├── lib/                          # 📦 Bundled dependencies (generated)
│   ├── requests/                 # HTTP library
│   ├── urllib3/                  # HTTP client
│   ├── certifi/                  # SSL certificates
│   ├── charset_normalizer/       # Text encoding
│   └── PIL/                      # Image processing
├── build/                        # 🔨 Build artifacts (temporary)
│   └── temp/                     # Downloaded packages
├── dist/                         # 📦 Final packages
│   └── runchat-blender-v1.1.0.zip # Ready for distribution
├── build.py                      # 🔧 Build script
├── clean.py                      # 🧹 Clean script
├── make.py                       # 🚀 Make script
├── validate_bundle.py            # ✅ Validation script
├── .gitignore                    # Git ignore rules
├── BUILD_GUIDE.md                # This guide
└── README_BUNDLING.md            # Quick reference
```

## Quick Start

### Using Make Script (Recommended)

```bash
cd runchat-blender/

# Build the addon
python make.py build

# Clean build artifacts
python make.py clean

# Validate bundled dependencies
python make.py validate

# Show help
python make.py help
```

### Direct Build Script

```bash
cd runchat-blender/
python build.py
```

## Build Process

The build process automatically:

1. **Downloads dependencies** - Gets `requests`, `Pillow`, and their dependencies
2. **Extracts packages** - Unzips wheel files to `lib/` directory
3. **Cleans up** - Removes unnecessary files (tests, docs, etc.)
4. **Validates** - Tests that all dependencies work correctly
5. **Creates package** - Generates final `.zip` file in `dist/` directory

## Output

After building, you'll find:

- **`lib/`** - Bundled dependencies (about 15-20 MB)
- **`dist/runchat-blender-v1.1.0.zip`** - Final package for users
- **`build/`** - Temporary build artifacts (can be deleted)

## Installation for Users

Users simply:
1. Download the `.zip` file from `runchat-blender/dist/`
2. Install it in Blender: Edit → Preferences → Add-ons → Install
3. Enable the "Runchat Blender Addon"

No additional setup required!

## Development Workflow

### For Active Development

```bash
# Clean previous builds
python make.py clean

# Make your code changes
# ...

# Build and test
python make.py build
python make.py validate

# Install in Blender for testing
# Use the zip file from runchat-blender/dist/
```

### Before Committing

```bash
# Clean build artifacts before committing
python make.py clean
git add .
git commit -m "Your changes"
```

The `lib/` directory is in `.gitignore` and won't be committed.

## Troubleshooting

### Build Fails

```bash
# Clean and try again
python make.py clean
python make.py build
```

### Dependencies Missing

```bash
# Check pip is available
python -m pip --version

# Update pip if needed
python -m pip install --upgrade pip

# Retry build
python make.py build
```

### Validation Fails

```bash
# Check what's in lib/
ls -la lib/

# Run validation with details
python validate_bundle.py
```

### Package Too Large

The bundled addon will be 15-20 MB, which is normal for a self-contained package. All dependencies are included.

## Manual Cleanup

If scripts fail, you can manually clean:

```bash
# Remove bundled dependencies
rm -rf lib/

# Remove build artifacts
rm -rf build/
rm -rf dist/

# Remove Python cache
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## Requirements

- Python 3.7+
- pip (for downloading dependencies)
- Internet connection (for downloading packages)

## Version Management

Version is automatically extracted from `bl_info["version"]` in `__init__.py`. Update there to change the package version.

## CI/CD Integration

For automated builds:

```bash
# In your CI script
cd runchat-blender/
python build.py

# Upload runchat-blender/dist/runchat-blender-v*.zip as release artifact
``` 