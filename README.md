# Runchat Blender Plugin

A comprehensive Blender plugin for integrating with Runchat workflows, providing a seamless interface to execute Runchat workflows directly from within Blender with full support for image uploads, viewport capture, and multiple output types.

## 🚀 Quick Start (30 seconds setup)

**New to Runchat?** No problem! Here's what you need:
1. A free Runchat account → [Sign up here](https://runchat.app/signup)
2. Blender 3.0+ installed
3. Python dependencies (auto-installed below)

**Installation:**
```bash
cd runchat-blender
python install.py
```

**First Run:**
1. Open Blender → `Edit > Preferences > Add-ons` → Enable "Runchat Blender Plugin"
2. Get your API key from [runchat.app/dashboard/keys](https://runchat.app/dashboard/keys)
3. Paste it in the addon preferences
4. Look for the Runchat panel in Properties → Scene
5. Try a workflow from the examples that auto-load!

## 💡 What Can You Do?

Transform your Blender workflows with AI:
- **Generate 3D models** from text descriptions or reference images
- **Enhance textures** using AI image processing
- **Auto-rig characters** with ML-powered rigging workflows  
- **Create animations** from pose sequences
- **Generate environments** from concept sketches
- **Process render outputs** for post-effects and style transfer

All without leaving Blender!

## 📋 Prerequisites

- **Blender**: Version 3.0 or higher
- **Python**: 3.7+ (usually bundled with Blender)
- **Internet Connection**: Required for API communication
- **Runchat Account**: Free signup at [runchat.app](https://runchat.app)
- **API Key**: Available in your dashboard after signup

### Python Dependencies
The following packages are auto-installed by `install.py`:
- `requests` - For API communication
- `Pillow` - For image processing
- `json` - For data handling (usually built-in)

## 📦 Installation

### Method 1: Auto-Install (Recommended)
```bash
# Clone the repository
git clone [repository-url]
cd runchat-blender

# Auto-install to Blender
python install.py
```

### Method 2: Manual Install
1. Download or clone this repository
2. In Blender, go to `Edit > Preferences > Add-ons`
3. Click `Install...` and select the addon folder or zip file
4. Enable the "Runchat Blender Plugin" addon
5. Configure your Runchat API key in the addon preferences

### Verify Installation
After installation, you should see:
- A new "Runchat" panel in Properties → Scene
- Example workflows automatically loaded
- No error messages in the Blender console

## ✨ Features

### Core Functionality
- **Workflow Integration**: Load and execute Runchat workflows by ID
- **Schema Loading**: Automatically fetch workflow schemas and configure inputs/outputs
- **Real-time Progress Tracking**: Visual progress indicators during execution
- **Instance Management**: Support for workflow instances and state management

### Input Support
- **Text Inputs**: Direct text entry for string parameters
- **Image Inputs**: Multiple input methods:
  - Viewport capture from current 3D view
  - File selection from disk
  - Automatic image upload to Runchat servers
- **Upload Status Tracking**: Real-time feedback on image upload progress

### Output Handling
- **Images**: View, save, and load output images into Blender
- **3D Models**: Import GLTF models directly into the scene
- **Text**: Display and copy text outputs
- **Mixed Outputs**: Handle workflows with multiple output types

### User Interface
- **Intuitive Panel**: Clean, organized interface in Properties panel
- **Collapsible Sections**: Organized inputs, outputs, and settings
- **Progress Indicators**: Visual feedback during all operations
- **Advanced Settings**: Optional advanced controls for power users

### Workflow Examples (New!)

The addon now automatically loads curated Blender workflow examples on startup:

- **Auto-discovery**: Examples are loaded automatically when the addon starts
- **One-click usage**: Click "Use" next to any example to load it instantly  
- **Refresh examples**: Use the refresh button to get the latest examples
- **Tagged workflows**: Examples show relevant tags like "blender", "3d", etc.

The examples are fetched from `https://runchat.app/api/v1/examples?plugin=blender` and display workflows specifically curated for Blender users.

## ⚙️ Setup

### API Key Configuration

1. **Get your API key** from [https://runchat.app/dashboard/keys](https://runchat.app/dashboard/keys)
2. **In Blender**, go to `Edit > Preferences > Add-ons`
3. **Find** "Runchat Blender Plugin" and expand its settings
4. **Enter** your API key in the "Runchat API Key" field
5. **Save** preferences

💡 **Tip:** Keep your API key secure and don't share it publicly!

## 📖 Usage Guide

### Your First Workflow

1. **Load a Workflow**:
   - Look at the auto-loaded examples in the panel
   - Click "Use" on any example to try it instantly
   - Or enter a custom Runchat workflow ID
   - Click the import icon to load the schema

2. **Configure Inputs**:
   - **Text Inputs**: Enter text directly in the value field
   - **Image Inputs**: Choose between:
     - **Viewport Capture**: Enable "Capture Viewport" to use current 3D view
     - **File Input**: Select an image file from disk
   - **Upload Progress**: Monitor image upload status in real-time

3. **Execute Workflow**:
   - Click "Execute Runchat" to run the workflow
   - Monitor progress through the progress bar and status messages
   - View detailed progress for image uploads and execution

4. **Handle Outputs**:
   - **Images**: 
     - Click "View" to load into Blender's image editor
     - Click "Save" to save to disk
   - **3D Models**: 
     - Click "Import" to import GLTF models into the scene
     - Click "Save" to save model files to disk
   - **Text**: 
     - View output text directly in the panel
     - Click "Copy" to copy to clipboard

### Advanced Features

#### Viewport Capture
The plugin can automatically capture your current Blender viewport:
- Position your 3D view as desired
- Enable "Capture Viewport" for image inputs
- Preview the capture before execution
- The current view will be uploaded when the workflow executes

#### Instance Management
- Workflows maintain state through instance IDs
- View current instance ID in advanced settings
- Click "New Instance" to start fresh
- Copy instance IDs for external reference
- Useful for workflows that build upon previous results

#### Progress Tracking
- Real-time progress bars during execution
- Detailed status messages for each operation phase
- Image upload progress with individual file tracking
- Error reporting with specific failure messages

#### Output Management
- **Auto Save**: Enable in settings to automatically save output images
- **Custom Paths**: Set custom directories for saving output files
- **Image Viewer**: Output images are automatically loaded into Blender's image editor
- **Model Import**: GLTF models are imported with proper material handling

## 🔧 Workflow Integration

### Supported Input Types
- `text`, `string`: Text input fields
- `image`, `file`: Image upload with viewport capture or file selection
- Mixed workflows with multiple input types

### Supported Output Types
- `image`: Base64 or URL-based images
- `gltf`, `model`, `3d`: 3D model files
- `text`, `string`: Text-based outputs
- JSON data structures with mixed content

### API Integration
The plugin uses the Runchat API v1:
- **Schema Endpoint**: `GET /{id}/schema` - Fetch workflow schema
- **Execution Endpoint**: `POST /{id}` - Execute workflow with inputs
- **Upload Endpoint**: `POST /upload/supabase` - Upload images

## 🔬 Development

### Development Setup

**Prerequisites:**
- Python 3.7+
- Blender 3.0+ with Python API access
- Git for version control
- Code editor (VS Code recommended)

**Quick Dev Setup:**
```bash
# Clone and setup
git clone [repository-url]
cd runchat-blender

# Install dev dependencies
pip install -r requirements-dev.txt  # if available

# Install plugin in development mode
python install.py --dev

# Enable Blender console for debugging
# In Blender: Window > Toggle System Console
```

### File Structure
```
runchat_blender_addon/
├── __init__.py          # Main addon registration
├── api.py              # API communication layer
├── preferences.py       # Addon preferences and API key management  
├── properties.py        # Blender property groups
├── operators/          # Operations organized by functionality
│   ├── __init__.py     # Operator registration
│   ├── execution.py    # Workflow execution
│   ├── schema.py       # Schema loading
│   ├── media.py        # Image/video/3D model operations
│   ├── upload.py       # File upload operations
│   └── utils.py        # General utility operations
├── ui/                 # User interface components
│   ├── __init__.py     # UI registration  
│   ├── panels.py       # Main UI panels
│   └── helpers.py      # UI helper functions
└── utils/              # Utility modules
    ├── __init__.py     # Utility imports
    ├── image_utils.py  # Image processing functions
    ├── model_utils.py  # 3D model operations
    ├── data_utils.py   # Data processing utilities
    └── blender_utils.py # Blender-specific utilities
```

### Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Test** your changes thoroughly in Blender
4. **Follow** Blender addon conventions and PEP 8 style guide
5. **Add** tests for new functionality
6. **Update** documentation as needed
7. **Submit** a pull request

### Testing

```bash
# Run unit tests (if available)
python -m pytest tests/

# Manual testing checklist:
# - Install addon in clean Blender instance
# - Test with different workflow types
# - Verify error handling
# - Check UI responsiveness
# - Test with different Blender versions
```

### API Integration Details

#### Input Formatting
Inputs are formatted as `paramId_nodeId` with appropriate values:
- Text inputs: Direct string values
- Image inputs: URLs from uploaded images

#### Output Processing
Outputs are processed based on data type and content:
- Images: Loaded into Blender or saved to disk
- Models: Imported as 3D objects with materials
- Text: Displayed in panels or copied to clipboard

#### Error Handling
The plugin implements comprehensive error handling:
- Network connectivity issues
- API authentication failures
- Invalid workflow IDs
- Upload timeouts
- Schema parsing errors

## 🐛 Troubleshooting

### Common Issues

1. **"Please set your Runchat API key"**
   - Ensure your API key is set in addon preferences
   - Verify the key is valid at [https://runchat.app/dashboard/keys](https://runchat.app/dashboard/keys)
   - Check that you saved the preferences after entering the key

2. **"Failed to load schema"**
   - Check that the Runchat ID is correct (try copying from browser URL)
   - Verify the workflow exists and is accessible
   - Check internet connection and firewall settings
   - Try refreshing examples to test connectivity

3. **"Upload failed"**
   - Ensure API key has upload permissions
   - Check image file size (max 10MB recommended)
   - Verify internet connection stability
   - Try with a smaller test image

4. **"Execution failed"**
   - Ensure all required inputs are provided
   - Check that input formats match the schema requirements
   - Verify uploaded images are accessible
   - Check Blender console for detailed error messages

5. **Viewport capture not working**
   - Ensure you have a valid 3D viewport active
   - Try switching to Material Preview or Rendered view
   - Check that OpenGL rendering is supported
   - Verify viewport has content to capture

6. **Plugin not visible after installation**
   - Check that the addon is enabled in preferences
   - Look for the panel in Properties → Scene (not Object)
   - Restart Blender if necessary
   - Check console for registration errors

### Debug Information
- **Blender Console**: `Window > Toggle System Console` for detailed error messages
- **Advanced Settings**: Enable for additional debugging options and instance management
- **Log Files**: Check Blender's console output for API request/response details
- **Test Connectivity**: Use the refresh examples button to verify API connection

### Getting Help

- **Documentation**: [https://docs.runchat.app](https://docs.runchat.app)
- **Community**: Join discussions on the Runchat community forums
- **Issues**: Report bugs on the GitHub repository
- **Feature Requests**: Submit ideas through the Runchat feedback system

## 📚 API Reference

### Input Types
- **Text**: `text_value` property for string inputs
- **Image**: `file_path` or `use_viewport_capture` for image inputs
- **Upload**: Automatic upload handling with status tracking

### Output Types
- **Image**: Base64 data or URLs, loaded into Blender
- **Model**: GLTF data, imported as 3D objects
- **Text**: String data, displayed in UI

### Progress Events
- Schema loading (0.3 progress)
- Image uploading (0.2-0.6 progress)
- Workflow execution (0.6-1.0 progress)
- Output processing (completion)

### Workflow States
- **Idle**: Ready for new workflow
- **Loading**: Fetching schema
- **Uploading**: Processing image uploads
- **Executing**: Running workflow
- **Processing**: Handling outputs
- **Complete**: Workflow finished
- **Error**: Something went wrong

## 🔗 Support and Links

- **Documentation**: [https://docs.runchat.app](https://docs.runchat.app)
- **Get API Keys**: [https://runchat.app/dashboard/keys](https://runchat.app/dashboard/keys)
- **Runchat Editor**: [https://runchat.app/editor](https://runchat.app/editor)
- **Workflow Gallery**: Browse public workflows at [https://runchat.app](https://runchat.app)
- **Community**: [Community forums and Discord](https://runchat.app/community)
- **Report Issues**: [GitHub Issues](https://github.com/[repo]/issues)

## 📄 License

This plugin is provided as-is for integration with Runchat workflows. Please refer to the Runchat terms of service for API usage guidelines. 