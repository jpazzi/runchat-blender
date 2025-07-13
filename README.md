# Runchat Blender Plugin

Blender addon for executing Runchat AI workflows directly from Blender.

## Quick Start

1. **Get API Key**: [runchat.app/signup/blender](https://runchat.app/signup/blender)
2. **Install**: Download `runchat-blender-v1.2.0.zip` → Blender → Edit → Preferences → Add-ons → Install
3. **Configure**: Enter API key in addon preferences
4. **Use**: Find Runchat panel in Properties → Scene

## Features

- Execute Runchat workflows from Blender
- Auto-capture viewport as input
- Upload images from files
- Import generated 3D models directly into scene
- View output images in Blender
- Auto-load workflow examples

## Usage

1. **Load Workflow**: Use examples or enter workflow ID
2. **Set Inputs**: Enter text or enable viewport capture for images
3. **Execute**: Click "Execute Runchat" 
4. **Get Results**: Images load automatically, models can be imported

## Troubleshooting

- **No API key error**: Set key in addon preferences
- **Schema load fails**: Check workflow ID and internet connection
- **Upload fails**: Verify API key permissions, check file size
- **Panel missing**: Enable addon in preferences, look in Properties → Scene

## Requirements

- Blender 3.0+
- Internet connection
- Runchat account and API key

## Development

### Building the Addon

To build the addon for distribution:

```bash
# Generate the package
python build.py

# The package will be created in dist/
ls dist/runchat-blender-v*.zip
```

### Creating a Release

To create a complete release with both package and repository index:

```bash
# Build package and generate repository index in one command
python scripts/release.py

# This will:
# 1. Clean previous builds
# 2. Build the addon package
# 3. Generate the official Blender repository index
# 4. Show next steps for publishing
```

### Debug Development

For development and debugging, run Blender with Python debugging enabled:

```bash
# macOS
/Applications/Blender.app/Contents/MacOS/Blender --debug-python

# Linux
blender --debug-python

# Windows
blender.exe --debug-python
```

This will show Python errors, import issues, and console output in the terminal, which is essential for development.

### Development Workflow

1. **Clone the repository**
2. **Make your changes** to the addon files
3. **Build the addon**: `python build.py`
4. **Install in Blender**: Use the zip from `dist/` folder
5. **Test with debug mode**: Run Blender with `--debug-python`
6. **Check console output** for errors or debug messages

### Release Workflow

1. **Create release**: `python scripts/release.py`
2. **Test the package** locally in Blender
3. **Commit and push**: `git add dist/ && git commit -m "Release vX.X.X" && git push`
4. **Create GitHub release** and upload the .zip file
5. **Repository is ready** at: `https://github.com/jpazzi/runchat-blender/raw/main/dist/index.json`

### Architecture

- **Dependencies**: Uses wheel-based dependencies in `wheels/` directory (handled automatically by Blender)
- **API Client**: `api.py` handles all Runchat API communication
- **UI**: `ui/` contains Blender panels and interface
- **Operators**: `operators/` contains Blender operators (actions/commands)
- **Properties**: `properties.py` defines data structures for Blender

### Logs and Debugging

- **Blender Console**: Window → Toggle System Console (Windows) or check terminal (macOS/Linux)
- **Python Console**: Blender → Scripting → Python Console
- **Debug Messages**: Run with `--debug-python` to see detailed error messages

## Links

- [Get API Key](https://runchat.app/signup/blender)
- [Documentation](https://docs.runchat.app)
- [Runchat App](https://runchat.app) 

## License

This plugin is licensed under the GNU General Public License v3.0 (GPL v3). See the [LICENSE.txt](LICENSE.txt) file for full license text.

**Important Note**: This plugin connects to the Runchat API, which is a separate service with its own terms of service. By using this plugin, you agree to both:
- The GPL v3 license for the plugin code
- Runchat's Terms of Service for the API service

This is an experimental tool. Use at your own risk.