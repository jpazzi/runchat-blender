# RunChat Blender Plugin

A comprehensive Blender plugin for integrating with RunChat workflows, providing a seamless interface to execute RunChat workflows directly from within Blender with full support for image uploads, viewport capture, and multiple output types.

## Features

### Core Functionality
- **Workflow Integration**: Load and execute RunChat workflows by ID
- **Schema Loading**: Automatically fetch workflow schemas and configure inputs/outputs
- **Real-time Progress Tracking**: Visual progress indicators during execution
- **Instance Management**: Support for workflow instances and state management

### Input Support
- **Text Inputs**: Direct text entry for string parameters
- **Image Inputs**: Multiple input methods:
  - Viewport capture from current 3D view
  - File selection from disk
  - Automatic image upload to RunChat servers
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

## Installation

1. Download or clone this repository
2. In Blender, go to `Edit > Preferences > Add-ons`
3. Click `Install...` and select the addon folder or zip file
4. Enable the "RunChat Blender Plugin" addon
5. Configure your RunChat API key in the addon preferences

## Setup

### API Key Configuration

1. Get your API key from [https://runchat.app/dashboard/keys](https://runchat.app/dashboard/keys)
2. In Blender, go to `Edit > Preferences > Add-ons`
3. Find "RunChat Blender Plugin" and expand its settings
4. Enter your API key in the "RunChat API Key" field

## Usage

### Basic Workflow

1. **Load a Workflow**:
   - Enter your RunChat workflow ID in the "RunChat ID" field
   - Click the import icon to load the schema
   - The workflow name and available inputs/outputs will be displayed

2. **Configure Inputs**:
   - **Text Inputs**: Enter text directly in the value field
   - **Image Inputs**: Choose between:
     - **Viewport Capture**: Enable "Capture Viewport" to use current 3D view
     - **File Input**: Select an image file from disk
   - **Upload Progress**: Monitor image upload status in real-time

3. **Execute Workflow**:
   - Click "Execute RunChat" to run the workflow
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

## Workflow Integration

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
The plugin uses the RunChat API v1:
- **Schema Endpoint**: `GET /{id}/schema` - Fetch workflow schema
- **Execution Endpoint**: `POST /{id}` - Execute workflow with inputs
- **Upload Endpoint**: `POST /upload/supabase` - Upload images

## Development

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

### Hot Reload Development
Enable "Development Mode" in the addon preferences for:
- Hot reload functionality
- Additional debugging features
- Development utilities

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

## Troubleshooting

### Common Issues

1. **"Please set your RunChat API key"**
   - Ensure your API key is set in addon preferences
   - Verify the key is valid at [https://runchat.app/dashboard/keys](https://runchat.app/dashboard/keys)

2. **"Failed to load schema"**
   - Check that the RunChat ID is correct
   - Verify the workflow exists and is accessible
   - Check internet connection and firewall settings

3. **"Upload failed"**
   - Ensure API key has upload permissions
   - Check image file size and format
   - Verify internet connection stability

4. **"Execution failed"**
   - Ensure all required inputs are provided
   - Check that input formats match the schema requirements
   - Verify uploaded images are accessible

5. **Viewport capture not working**
   - Ensure you have a valid 3D viewport active
   - Try switching to a 3D view before capturing
   - Check that OpenGL rendering is supported

### Debug Information
- Check Blender's console (`Window > Toggle System Console`) for detailed error messages
- Enable "Advanced Settings" for additional debugging options
- Use the example scripts for testing functionality

## API Reference

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

## Support and Links

- **Documentation**: [https://docs.runchat.app](https://docs.runchat.app)
- **API Keys**: [https://runchat.app/dashboard/keys](https://runchat.app/dashboard/keys)
- **RunChat Editor**: [https://runchat.app/editor](https://runchat.app/editor)
- **Workflow Gallery**: Browse public workflows at [https://runchat.app](https://runchat.app)

## License

This plugin is provided as-is for integration with RunChat workflows. Please refer to the RunChat terms of service for API usage guidelines. 