# Quick Build Guide - AUTOMATED!

**⚠️ This addon REQUIRES bundled dependencies and will NOT work without them!**

## TL;DR - Automated Build Process

**Just run one command:**

```bash
cd runchat-blender/
python make.py build
```

That's it! The build script automatically:
- Downloads all required dependencies
- Bundles them into the `lib/` folder
- Creates a ready-to-distribute package in `dist/`

## Alternative Commands

```bash
# Build the addon
python make.py build

# Clean build artifacts
python make.py clean

# Validate dependencies
python make.py validate

# Show help
python make.py help
```

## Expected Result

✅ Bundled Requests: bundled  
✅ Bundled PIL/Pillow: Available  
✅ All bundled dependencies working perfectly  
📦 Package created: `runchat-blender/dist/runchat-blender-v1.1.0.zip`

## For Users

Download the pre-built package from the `runchat-blender/dist/` folder and install it directly in Blender. No additional setup required!

## No Manual Work Required!

The automated build system handles all the complexity. See `BUILD_GUIDE.md` for detailed information. 