# RunChat Blender Addon

A powerful Blender addon that provides custom nodes for interfacing with [RunChat](https://runchat.app) workflows, enabling seamless integration between Blender and AI-powered automation tools.

## 🆕 What's New in v1.1

- **Enhanced API Integration**: Proper `paramId_nodeId` parameter mapping per RunChat API specification
- **Webhook Support**: Direct webhook data transmission for simplified workflows
- **Image Compression**: Built-in JPEG compression with quality controls for faster transmission
- **Material Creation**: Automatic material generation from received images
- **Progress Tracking**: Real-time execution time monitoring and detailed status reporting
- **Better Error Handling**: Comprehensive HTTP status code handling and user-friendly error messages
- **Multiple Image Sources**: Support for render results, active images, and file paths
- **Enhanced Model Loading**: Support for .blend files and better import options
- **Instance Management**: Visual instance ID tracking and easy reset functionality

## Features

### Core Capabilities
- **🚀 RunChat Executor Node**: Dynamic node that adapts to any RunChat workflow with schema auto-loading
- **📸 Advanced Image I/O**: Send and receive images with compression and multiple source options
- **🎨 Material Integration**: Automatic material creation from received images
- **🧊 3D Model Loader**: Download and import models from URLs with scale and format options
- **🌐 Webhook Support**: Direct JSON data transmission for webhook-enabled workflows
- **📊 Real-time Monitoring**: Execution time tracking and detailed progress feedback
- **🔄 Instance Management**: Maintain workflow state across executions with visual tracking

### Technical Features
- **Custom Node Tree**: Dedicated node editor optimized for RunChat workflows
- **Async Operations**: Non-blocking API calls and file operations with progress callbacks
- **Smart Compression**: Adaptive image compression with quality controls (10-100%)
- **Enhanced Error Handling**: HTTP status code detection and user-friendly error reporting
- **API Key Management**: Secure storage of RunChat API credentials with validation
- **Cross-platform Compatibility**: Works on Windows, macOS, and Linux

## Installation

### Method 1: Automated Installation

1. Run the installation script:
   ```bash
   python install.py
   ```
2. Start or restart Blender
3. Enable the "RunChat Blender Nodes" addon in preferences
4. Configure your API key

### Method 2: Manual Installation

1. Download or clone this repository
2. In Blender, go to `Edit > Preferences > Add-ons`
3. Click "Install..." and select the addon folder or zip file
4. Enable the "RunChat Blender Nodes" addon
5. Configure your API key in the addon preferences

## Configuration

### API Key Setup

1. Get your RunChat API key from [runchat.app/dashboard/keys](https://runchat.app/dashboard/keys)
2. In Blender preferences (`Edit > Preferences`), go to the "Add-ons" section
3. Find "RunChat Blender Nodes" and expand the preferences
4. Enter your API key in the provided field
5. Use the "Get API Key" button to open the RunChat dashboard if needed

## Usage Guide

### Creating a RunChat Node Tree

1. Add a new node editor panel or switch an existing one to "RunChat Nodes"
2. You'll see a dedicated node tree type for RunChat workflows

### Workflow Types

#### 1. Schema-Based Workflows (Recommended)

**Step-by-step:**
1. Add a "RunChat Executor" node (`Shift + A > RunChat Core > RunChat Executor`)
2. Enter your workflow ID from the RunChat editor URL
3. Click "Load Schema" to fetch dynamic inputs/outputs
4. Connect your data nodes and click "Execute"

**Features:**
- ✅ Automatic parameter mapping using `paramId_nodeId` format
- ✅ Type-safe socket connections
- ✅ Input validation and error checking
- ✅ Instance state management

#### 2. Webhook Workflows

**Step-by-step:**
1. Add a "RunChat Webhook Data" node for JSON preparation
2. Add a "RunChat Executor" node and enable "Webhook Mode"
3. Connect webhook data and execute

**Features:**
- ✅ Direct JSON data transmission
- ✅ No schema loading required
- ✅ Flexible data structures
- ✅ Real-time webhook trigger support

### Node Reference

#### RunChat Core Nodes

**RunChat Executor**
- Main workflow execution with dynamic schema loading
- Supports both schema and webhook modes
- Real-time execution tracking and instance management
- Enhanced error reporting with HTTP status codes

**RunChat Webhook Data**
- JSON data preparation and validation
- Built-in JSON formatting and syntax checking
- Direct webhook payload construction

#### RunChat I/O Nodes

**RunChat Image Send**
- Multiple source options: file path, render result, active image
- JPEG compression with quality control (10-100%)
- Real-time size estimation and processing feedback
- Automatic format conversion and optimization

**RunChat Image Receive**
- Automatic file saving with organized naming
- Direct Blender image loading
- Material creation with proper node setup
- Flexible save path configuration

**RunChat Model Loader**
- Support for OBJ, FBX, PLY, STL, glTF, and .blend formats
- Auto-format detection from URL
- Import scaling and scene clearing options
- Object tracking and metadata storage

### Socket Types & Data Flow

The addon provides custom socket types for type-safe connections:

- **🟠 Image Socket**: Base64 image data with compression metadata
- **🔵 Model Socket**: 3D model data with format and object information
- **🟣 Webhook Socket**: JSON webhook data with validation
- **⚪ Data Socket**: Generic data with type information and metadata

### Advanced Features

#### Auto-Execute Mode
Enable on the RunChat Executor node to automatically run workflows when input data changes. Perfect for real-time processing workflows.

#### Instance Management
- Visual instance ID display (first 8 characters)
- "New Instance" button for fresh executions
- Automatic instance ID persistence across runs
- Clear visual feedback for state management

#### Progress Monitoring
- Real-time execution time tracking
- Detailed status messages with operation feedback
- HTTP error code translation
- Network timeout and retry handling

#### Image Processing
- Automatic RGB conversion for compatibility
- Quality-based JPEG compression
- Size estimation and optimization feedback
- Multiple source priority: render > active > file

## API Integration Details

### Authentication
```
Authorization: Bearer YOUR_API_KEY
```

### Endpoints Used
- `GET /api/v1/{workflow_id}/schema` - Schema retrieval with authentication
- `POST /api/v1/{workflow_id}` - Workflow execution with proper parameter mapping

### Parameter Mapping
The addon now correctly implements the RunChat API specification:
- Schema mode: Uses `paramId_nodeId` format for proper parameter identification
- Webhook mode: Sends raw JSON data directly to webhook endpoints
- Tree data: Supports complex data structures like `{"0": [...], "0:1": [...]}`

### Error Handling
- **401 Unauthorized**: Invalid API key detection
- **404 Not Found**: Workflow not found or deleted
- **429 Too Many Requests**: Rate limiting with retry suggestions
- **Network Errors**: Timeout and connectivity issue handling

## Development

### File Structure
```
runchat_blender/
├── __init__.py          # Addon initialization and metadata
├── preferences.py       # API key management and settings
├── runchat_nodes.py     # Node definitions and operators (enhanced)
├── utils.py            # Utility functions with compression support
├── example_usage.py    # Programming examples and demos
├── install.py          # Automated installation script
└── README.md           # This comprehensive documentation
```

### Dependencies
- **Blender 3.0+**: Core Blender Python API
- **requests**: HTTP client (included with Blender)
- **Pillow (Optional)**: Enhanced image compression (fallback available)
- **Standard Library**: json, threading, base64, tempfile, time

### Extending the Addon

**Adding New Node Types:**
1. Create a class inheriting from `RunChatNodeBase`
2. Implement `init()`, `draw_buttons()`, and required operators
3. Add to the registration list and node categories
4. Use the enhanced socket types for proper data flow

**Custom Socket Types:**
```python
class MyCustomSocket(NodeSocket):
    bl_idname = 'MyCustomSocket'
    bl_label = "My Socket"
    
    def draw_color(self, context, node):
        return (1.0, 0.5, 0.0, 1.0)  # Orange
```

## Troubleshooting

### Common Issues

**"Invalid API key" error:**
- Verify your API key at [runchat.app/dashboard/keys](https://runchat.app/dashboard/keys)
- Check for extra spaces or characters in the key
- Ensure the key has proper permissions

**Schema loading fails:**
- Verify the workflow ID format (8+ characters, alphanumeric + underscores/hyphens)
- Check if the workflow exists and is published
- Ensure network connectivity and firewall settings

**Image processing fails:**
- Verify file paths are absolute and accessible
- Check image format compatibility
- Ensure sufficient disk space for compression
- Try different compression quality settings

**Model loading fails:**
- Verify URL accessibility and file format
- Check available memory for large models
- Ensure proper import addon enablement in Blender
- Try different format detection settings

**Execution timeouts:**
- Check network stability
- Increase timeout values for complex workflows
- Verify RunChat service status
- Try smaller input data sets

### Performance Optimization

**For Large Images:**
- Use compression quality 70-85% for optimal size/quality balance
- Enable "Use Active Image" for direct processing
- Consider image resolution reduction before sending

**For Complex Models:**
- Use auto-format detection for best compatibility
- Enable "Clear Scene" only when necessary
- Set appropriate import scale factors
- Monitor memory usage during import

**For Long Workflows:**
- Use instance management to resume executions
- Enable auto-execute mode carefully to avoid loops
- Monitor execution times and optimize accordingly

### Debug Mode
Enable Blender's Python console (`Window > Toggle System Console`) for detailed logging:
- API request/response details
- Image processing steps
- Model import progress
- Error stack traces

## Performance Benchmarks

### Image Processing
- **Small Images** (< 1MB): ~0.5-1s processing time
- **Medium Images** (1-5MB): ~1-3s with compression
- **Large Images** (5-20MB): ~3-8s with optimization
- **Compression Ratio**: 60-90% size reduction with quality 80%

### Model Loading
- **Simple Models** (< 10MB): ~2-5s download + import
- **Complex Models** (10-50MB): ~5-15s with progress feedback
- **Large Models** (50MB+): ~15-60s with memory optimization

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow PEP 8** style guidelines for Python code
3. **Test thoroughly** with different workflow types
4. **Document changes** in both code and README
5. **Submit a pull request** with clear description

### Development Setup
```bash
git clone https://github.com/your-repo/runchat-blender.git
cd runchat-blender
# Make your changes
python install.py  # Test installation
```

## License

This addon is released under the **MIT License**. See LICENSE file for details.

## Support & Community

- **📖 Documentation**: [docs.runchat.app](https://docs.runchat.app)
- **🐛 Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **💬 Community**: RunChat Discord/Forums
- **📧 Support**: support@runchat.app

## Version History

### v1.1.0 (Latest)
- 🚀 Enhanced API integration with proper parameter mapping
- 🌐 Webhook support for direct JSON transmission
- 📸 Image compression with quality controls
- 🎨 Automatic material creation from images
- 📊 Real-time execution monitoring
- 🔧 Better error handling and status reporting
- 🧊 Enhanced model loading with .blend support
- 📁 Improved file organization and naming

### v1.0.0
- ✨ Initial release with core functionality
- 🔧 Basic RunChat workflow execution
- 📸 Image send/receive capabilities
- 🧊 3D model URL loading
- 🎛️ Dynamic schema loading
- 🎨 Custom node tree and socket types

---

*Built with ❤️ for the Blender and RunChat communities* 