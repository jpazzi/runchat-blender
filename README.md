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