import bpy
import base64
import os
import tempfile
from typing import Any, Dict, Optional
import bmesh

# Optional PIL import with fallback
try:
    from PIL import Image
    PIL_AVAILABLE = True
    print("✅ PIL/Pillow available - enhanced image compression enabled")
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL/Pillow not available - using basic image processing")

import io

def image_to_base64(image_path: str, quality: int = 90) -> Optional[str]:
    """Convert an image file to base64 string with optional compression"""
    try:
        if PIL_AVAILABLE:
            # Enhanced compression with PIL
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (removes alpha channel)
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                
                # Save to bytes with compression
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                image_bytes = buffer.getvalue()
                
                # Encode to base64
                encoded_string = base64.b64encode(image_bytes).decode('utf-8')
                return encoded_string
        else:
            # Fallback without PIL compression
            print("Using basic image encoding (no compression)")
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
            
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def base64_to_image(base64_string: str, output_path: str, filename: str = None) -> Optional[str]:
    """Convert base64 string to image file"""
    try:
        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            existing_files = [f for f in os.listdir(output_path) if f.startswith('runchat_image_')]
            filename = f"runchat_image_{len(existing_files):04d}.png"
        
        full_path = os.path.join(output_path, filename)
        
        # Decode and save
        image_data = base64.b64decode(base64_string)
        with open(full_path, 'wb') as image_file:
            image_file.write(image_data)
            
        return full_path
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def blender_image_to_base64(image_name: str, quality: int = 90) -> Optional[str]:
    """Convert a Blender image to base64 with compression"""
    try:
        image = bpy.data.images.get(image_name)
        if not image:
            return None
        
        # Save image to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Save the image
        original_format = image.file_format
        image.file_format = 'PNG'
        image.save_render(temp_path)
        image.file_format = original_format
        
        # Convert to base64 with compression
        base64_string = image_to_base64(temp_path, quality)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return base64_string
    except Exception as e:
        print(f"Error converting Blender image: {e}")
        return None

def load_image_from_base64(base64_string: str, image_name: str = "RunChat_Image") -> Optional[bpy.types.Image]:
    """Load base64 image into Blender"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Decode base64 to file
        image_data = base64.b64decode(base64_string)
        with open(temp_path, 'wb') as f:
            f.write(image_data)
        
        # Load into Blender
        image = bpy.data.images.load(temp_path)
        image.name = image_name
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return image
    except Exception as e:
        print(f"Error loading image into Blender: {e}")
        return None

def get_active_render_image() -> Optional[str]:
    """Get the current render result as base64"""
    try:
        # Get render result
        render_result = bpy.data.images.get('Render Result')
        if not render_result:
            return None
        
        return blender_image_to_base64('Render Result')
    except Exception as e:
        print(f"Error getting render image: {e}")
        return None

def get_active_image_editor_image() -> Optional[str]:
    """Get the active image from Image Editor as base64"""
    try:
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                if area.spaces.active.image:
                    return blender_image_to_base64(area.spaces.active.image.name)
        return None
    except Exception as e:
        print(f"Error getting active image: {e}")
        return None

def mesh_to_obj_string(obj_name: str) -> Optional[str]:
    """Convert a Blender mesh object to OBJ format string"""
    try:
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != 'MESH':
            return None
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.obj', mode='w+', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Store current selection
        original_selection = bpy.context.selected_objects.copy()
        original_active = bpy.context.view_layer.objects.active
        
        # Select only this object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Export to OBJ
        bpy.ops.export_scene.obj(
            filepath=temp_path,
            use_selection=True,
            use_materials=False,
            use_uvs=True,
            use_normals=True
        )
        
        # Read the file content
        with open(temp_path, 'r') as f:
            obj_content = f.read()
        
        # Restore selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj_sel in original_selection:
            obj_sel.select_set(True)
        bpy.context.view_layer.objects.active = original_active
        
        # Clean up
        os.unlink(temp_path)
        
        return obj_content
    except Exception as e:
        print(f"Error converting mesh to OBJ: {e}")
        return None

def extract_socket_value(socket) -> Any:
    """Extract value from a Blender node socket with improved handling"""
    try:
        if not socket.is_linked:
            # Return default value if not connected
            if hasattr(socket, 'default_value'):
                return socket.default_value
            return None
        
        # Get linked socket
        linked_socket = socket.links[0].from_socket
        from_node = linked_socket.node
        
        # Handle different socket types
        if socket.bl_idname == 'NodeSocketString':
            return str(linked_socket.default_value) if hasattr(linked_socket, 'default_value') else ""
        elif socket.bl_idname == 'NodeSocketFloat':
            return float(linked_socket.default_value) if hasattr(linked_socket, 'default_value') else 0.0
        elif socket.bl_idname == 'NodeSocketInt':
            return int(linked_socket.default_value) if hasattr(linked_socket, 'default_value') else 0
        elif socket.bl_idname == 'NodeSocketBool':
            return bool(linked_socket.default_value) if hasattr(linked_socket, 'default_value') else False
        elif socket.bl_idname == 'NodeSocketVector':
            return list(linked_socket.default_value) if hasattr(linked_socket, 'default_value') else [0.0, 0.0, 0.0]
        elif socket.bl_idname == 'NodeSocketColor':
            return list(linked_socket.default_value) if hasattr(linked_socket, 'default_value') else [1.0, 1.0, 1.0, 1.0]
        elif socket.bl_idname == 'RunChatImageSocket':
            # Handle image data
            if hasattr(from_node, 'image_data'):
                return from_node.image_data
            return None
        elif socket.bl_idname == 'RunChatModelSocket':
            # Handle model data
            if hasattr(from_node, 'model_data'):
                return from_node.model_data
            return None
        elif socket.bl_idname == 'RunChatWebhookSocket':
            # Handle webhook data
            if hasattr(from_node, 'webhook_data'):
                return from_node.webhook_data
            return None
        else:
            # Generic data socket - try to get stored output data
            output_attr = f"output_{linked_socket.name}"
            if hasattr(from_node, output_attr):
                return getattr(from_node, output_attr)
            return None
            
    except Exception as e:
        print(f"Error extracting socket value: {e}")
        return None

def format_data_for_runchat(data: Any, data_type: str = 'auto') -> Any:
    """Format data for RunChat API consumption with enhanced handling"""
    try:
        if data_type == 'image' or (data_type == 'auto' and isinstance(data, str) and len(data) > 100):
            # Enhanced image data formatting
            return {
                'type': 'image',
                'format': 'base64',
                'data': data,
                'metadata': {
                    'size': len(data),
                    'source': 'blender'
                }
            }
        elif data_type == 'model':
            # Enhanced model data formatting
            if isinstance(data, dict):
                return {
                    'type': 'model',
                    'format': data.get('file_format', 'obj'),
                    'data': data,
                    'metadata': {
                        'source': 'blender',
                        'objects': data.get('imported_objects', [])
                    }
                }
            else:
                return {
                    'type': 'model',
                    'format': 'obj',
                    'data': data
                }
        elif data_type == 'webhook':
            # Handle webhook data
            if isinstance(data, str):
                try:
                    import json
                    return json.loads(data)
                except json.JSONDecodeError:
                    return {'raw_data': data}
            return data
        else:
            # Return as-is for basic types with metadata
            return {
                'type': 'primitive',
                'data': data,
                'metadata': {
                    'source': 'blender',
                    'data_type': type(data).__name__
                }
            }
    except Exception as e:
        print(f"Error formatting data: {e}")
        return data

def process_runchat_output(output_data: Dict[str, Any]) -> Any:
    """Process output data from RunChat API with enhanced handling"""
    try:
        if isinstance(output_data, dict):
            data_type = output_data.get('type', 'unknown')
            
            if data_type == 'image':
                # Handle image data
                format_type = output_data.get('format', 'base64')
                if format_type == 'base64':
                    return output_data.get('data', '')
                elif format_type == 'url':
                    # Download image from URL and convert to base64
                    import requests
                    try:
                        response = requests.get(output_data.get('data', ''), timeout=30)
                        if response.status_code == 200:
                            return base64.b64encode(response.content).decode('utf-8')
                    except:
                        pass
                    return None
                    
            elif data_type == 'model':
                # Handle model data with metadata
                model_data = output_data.get('data', '')
                metadata = output_data.get('metadata', {})
                
                return {
                    'model_content': model_data,
                    'format': output_data.get('format', 'obj'),
                    'metadata': metadata
                }
                
            elif data_type == 'url':
                # Handle URL data
                return output_data.get('data', '')
                
            elif data_type == 'primitive':
                # Handle primitive data with metadata
                return output_data.get('data')
                
        # Return as-is if not a recognized format
        return output_data
        
    except Exception as e:
        print(f"Error processing RunChat output: {e}")
        return output_data

def validate_workflow_id(workflow_id: str) -> bool:
    """Validate RunChat workflow ID format with enhanced checks"""
    if not workflow_id:
        return False
    
    # Basic validation - adjust based on actual RunChat ID format
    if len(workflow_id) < 8:
        return False
    
    # Check for valid characters (alphanumeric and some special chars)
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', workflow_id):
        return False
    
    return True

def get_blender_version_info() -> Dict[str, Any]:
    """Get Blender version information for API requests"""
    return {
        'blender_version': '.'.join(map(str, bpy.app.version)),
        'addon_version': '1.0.0',  # This should match the version in bl_info
        'platform': bpy.app.build_platform.decode('utf-8'),
        'python_version': f"{bpy.app.version_string}"
    }

def create_progress_callback(node, operation_name: str):
    """Create a progress callback function for long operations"""
    def update_progress(progress: float, message: str = ""):
        if hasattr(node, 'status'):
            node.status = f"{operation_name}: {progress:.0%}" + (f" - {message}" if message else "")
    
    return update_progress

def handle_tree_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tree-structured data for RunChat API"""
    try:
        # Convert Grasshopper-style tree data to RunChat format
        if isinstance(data, dict):
            tree_data = {}
            for key, value in data.items():
                # Handle path-based keys like "0", "0:1", "1:2:3"
                if isinstance(value, list):
                    tree_data[key] = value
                else:
                    tree_data[key] = [value]
            return tree_data
        return data
    except Exception as e:
        print(f"Error handling tree data: {e}")
        return data

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility"""
    import re
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Trim and ensure it's not empty
    sanitized = sanitized.strip('_. ')
    return sanitized if sanitized else 'unnamed'

def get_material_from_image(image_name: str) -> Optional[bpy.types.Material]:
    """Create or get existing material for an image"""
    try:
        image = bpy.data.images.get(image_name)
        if not image:
            return None
        
        material_name = f"Material_{sanitize_filename(image_name)}"
        
        # Check if material already exists
        material = bpy.data.materials.get(material_name)
        if material:
            return material
        
        # Create new material
        material = bpy.data.materials.new(material_name)
        material.use_nodes = True
        
        # Clear default nodes
        material.node_tree.nodes.clear()
        
        # Add shader nodes
        bsdf = material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
        tex_image = material.node_tree.nodes.new('ShaderNodeTexImage')
        
        # Set positions
        bsdf.location = (0, 0)
        output.location = (300, 0)
        tex_image.location = (-300, 0)
        
        # Set image
        tex_image.image = image
        
        # Connect nodes
        material.node_tree.links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
        material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        return material
        
    except Exception as e:
        print(f"Error creating material from image: {e}")
        return None 