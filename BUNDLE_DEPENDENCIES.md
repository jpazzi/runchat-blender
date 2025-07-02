# Bundling Dependencies for Runchat Blender Addon

This addon **requires** bundled dependencies to function. It will not work without them.

## Required Dependencies

The Runchat Blender addon **always uses** these bundled Python packages:
- `requests` - For HTTP API calls
- `Pillow` (PIL) - For image processing

## Download Pre-bundled Release (Recommended)

The easiest way is to download a pre-bundled release from the official releases page which already includes all dependencies.

## Manual Bundling (For Developers)

If you need to bundle dependencies yourself:

### Step 1: Download Dependencies

Create a temporary directory and download the packages:

```bash
mkdir temp_deps
cd temp_deps

# Download requests and its dependencies
pip download requests --dest .

# Download Pillow
pip download Pillow --dest .
```

### Step 2: Extract and Organize

1. Extract each `.whl` file:
   ```bash
   # For each .whl file:
   unzip filename.whl
   ```

2. Create the lib directory in your addon:
   ```
   runchat-blender/
   ├── lib/
   │   ├── requests/
   │   ├── urllib3/
   │   ├── certifi/
   │   ├── charset_normalizer/
   │   └── PIL/
   ├── __init__.py
   └── ... (other addon files)
   ```

3. Copy the extracted package folders to `runchat-blender/lib/`:
   - Copy `requests/` folder
   - Copy `urllib3/` folder  
   - Copy `certifi/` folder
   - Copy `charset_normalizer/` folder
   - Copy `PIL/` folder

### Step 3: Clean Up

Remove unnecessary files to reduce addon size:

```bash
cd runchat-blender/lib/

# Remove all .dist-info folders
find . -name "*.dist-info" -type d -exec rm -rf {} +

# Remove test files
find . -name "test*" -type d -exec rm -rf {} +
find . -name "*test*" -type d -exec rm -rf {} +

# Remove __pycache__ folders
find . -name "__pycache__" -type d -exec rm -rf {} +

# Remove .pyc files
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
```

### Step 4: Test the Bundle

1. Zip your addon folder
2. Install in Blender
3. Check the console for dependency loading messages:
   - `[Runchat] Added bundled dependencies: /path/to/lib`
   - `[Runchat API] Using HTTP backend: requests` (or fallback)

## File Structure After Bundling

```
runchat-blender.zip
├── runchat-blender/
│   ├── __init__.py              # Includes dependency path setup
│   ├── lib/                     # Bundled dependencies
│   │   ├── requests/
│   │   ├── urllib3/
│   │   ├── certifi/
│   │   ├── charset_normalizer/
│   │   └── PIL/
│   ├── api.py
│   ├── properties.py
│   ├── operators/
│   ├── ui/
│   └── utils/
│       └── dependencies.py     # Dependency manager
```

## No Fallback Behavior

**IMPORTANT**: This addon requires bundled dependencies and will not work without them:

1. **With bundled dependencies**: Full functionality
2. **Without bundled dependencies**: Addon will fail to load and show error messages

The addon will show clear error messages if dependencies are missing.

## Troubleshooting

### Dependencies Not Loading
- Check Blender console for path messages
- Verify `lib/` folder exists in addon directory
- Check file permissions

### Import Errors
- Ensure all dependency subfolders are present
- Check for missing `__init__.py` files in packages
- Verify Python version compatibility

### Size Optimization

To reduce addon size:
1. Remove documentation folders (`docs/`, `examples/`)
2. Keep only essential `.py` files
3. Remove locale/translation files if present
4. Use Python wheel files for platform-specific builds

## Version Compatibility

- **Blender 3.0+**: Supports Python 3.9+
- **Blender 2.8-2.93**: Supports Python 3.7-3.9
- Ensure dependency versions match your target Python version

## Security Notes

- Only bundle dependencies from trusted sources
- Verify package integrity before bundling
- Consider using `pip-audit` to check for vulnerabilities 