# utils/image_utils.py

import bpy
import base64
import os
import tempfile
import io
from typing import Any, Dict, Optional

# Import dependencies lazily to avoid path issues during module loading
_pil_image = None
_pil_available = None
_requests = None

def get_pil_module():
    """Get the PIL module, importing it lazily"""
    global _pil_image, _pil_available
    if _pil_image is None:
        from .dependencies import get_pil
        _pil_image, _pil_available = get_pil()
    return _pil_image, _pil_available

def get_requests_module():
    """Get the requests module, importing it lazily"""
    global _requests
    if _requests is None:
        from .dependencies import get_requests
        _requests, _ = get_requests()
    return _requests


def image_to_base64(image_path: str, quality: int = 90) -> Optional[str]:
    """Convert an image file to base64 string with optional compression"""
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return None
    
    try:
        PIL_Image, PIL_AVAILABLE = get_pil_module()
        if PIL_AVAILABLE:
            # Load and potentially compress the image
            with PIL_Image.open(image_path) as img:
                # Convert to RGB if necessary (removes alpha channel)
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = PIL_Image.new('RGB', img.size, (255, 255, 255))
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
            print("PIL not available, using basic encoding")
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
                
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None


def base64_to_image(base64_string: str, output_path: str, filename: str = None) -> Optional[str]:
    """Convert base64 string to image file"""
    if not base64_string:
        print("Empty base64 string provided")
        return None
    
    try:
        from .data_utils import sanitize_filename
        
        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
                    existing_files = [f for f in os.listdir(output_path) if f.startswith('Runchat_image_')]
        filename = f"Runchat_image_{len(existing_files):04d}.png"
        
        # Sanitize filename
        filename = sanitize_filename(filename)
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
    temp_path = None
    try:
        image = bpy.data.images.get(image_name)
        if not image:
            print(f"Image '{image_name}' not found in Blender data")
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
        
        return base64_string
    except Exception as e:
        print(f"Error converting Blender image: {e}")
        return None
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError as e:
                print(f"Warning: Could not delete temp file {temp_path}: {e}")


def load_image_from_base64(base64_string: str, image_name: str = "RunChat_Image") -> Optional[bpy.types.Image]:
    """Load base64 image into Blender"""
    if not base64_string:
        print("Empty base64 string provided")
        return None
    
    temp_path = None
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
        
        return image
    except Exception as e:
        print(f"Error loading image into Blender: {e}")
        return None
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError as e:
                print(f"Warning: Could not delete temp file {temp_path}: {e}")


def load_image_from_url(url: str, image_name: str = "RunChat_Image", operator=None) -> Optional[bpy.types.Image]:
    """Load image from URL into Blender"""
    def report_info(msg):
        if operator and hasattr(operator, 'report'):
            operator.report({'INFO'}, msg)
        else:
            print(f"[Runchat] {msg}")
    
    def report_error(msg):
        if operator and hasattr(operator, 'report'):
            operator.report({'ERROR'}, msg)
        else:
            print(f"[Runchat ERROR] {msg}")
    
    if not url or not url.startswith('http'):
        report_error(f"Invalid URL provided: {url}")
        return None
    
    temp_path = None
    try:
        report_info(f"Downloading image from URL: {url[:100]}...")
        
        # Determine file extension from URL
        file_extension = '.png'  # default
        url_lower = url.lower()
        if url_lower.endswith('.jpg') or url_lower.endswith('.jpeg'):
            file_extension = '.jpg'
        elif url_lower.endswith('.png'):
            file_extension = '.png'
        elif url_lower.endswith('.gif'):
            file_extension = '.gif'
        elif url_lower.endswith('.webp'):
            file_extension = '.webp'
        elif url_lower.endswith('.bmp'):
            file_extension = '.bmp'
        elif url_lower.endswith('.tiff') or url_lower.endswith('.tif'):
            file_extension = '.tiff'
        
        report_info(f"Detected file extension: {file_extension}")
        
        # Download the image
        response = get_requests_module().get(url, timeout=30)
        response.raise_for_status()
        
        if len(response.content) == 0:
            report_error("Downloaded image has no content")
            return None
        
        report_info(f"Downloaded {len(response.content)} bytes")
        
        # Create temporary file with correct extension
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp_file:
            temp_path = tmp_file.name
            tmp_file.write(response.content)
        
        report_info(f"Saved to temp file: {temp_path}")
        
        # Verify temp file exists and has content
        if not os.path.exists(temp_path):
            report_error("Temp file was not created")
            return None
            
        temp_size = os.path.getsize(temp_path)
        if temp_size == 0:
            report_error("Temp file is empty")
            return None
            
        report_info(f"Temp file size: {temp_size} bytes")
        
        # Load into Blender
        report_info("Loading image into Blender...")
        image = bpy.data.images.load(temp_path)
        
        # Set the name
        image.name = image_name
        
        # Force Blender to fully load and process the image data
        report_info("Forcing image data load...")
        image.reload()
        
        # Try accessing the pixels to force loading
        try:
            # This forces Blender to actually load the pixel data
            width, height = image.size
            if width > 0 and height > 0:
                report_info(f"Image dimensions validated: {width}x{height}")
                # Try to access first pixel to ensure data is loaded
                if len(image.pixels) > 0:
                    report_info("Image pixel data confirmed")
                else:
                    report_info("Image has no pixel data")
            else:
                report_error("Image has invalid dimensions")
                bpy.data.images.remove(image)
                return None
        except Exception as pixel_error:
            report_error(f"Error accessing image pixels: {pixel_error}")
            bpy.data.images.remove(image)
            return None
        
        # Verify the image has data one more time
        if not image.has_data:
            report_info("Image loaded but has no data - trying pack operation")
            try:
                image.pack()
                # Check again after packing
                if image.has_data:
                    report_info("Pack operation successful - image now has data")
                else:
                    report_error("Pack operation failed - image still has no data")
                    bpy.data.images.remove(image)
                    return None
            except Exception as pack_error:
                report_error(f"Pack operation failed with error: {pack_error}")
                bpy.data.images.remove(image)
                return None
        
        report_info(f"Successfully loaded image '{image.name}' with size {image.size[0]}x{image.size[1]}")
        return image
        
    except Exception as e:
        report_error(f"Error loading image from URL: {e}")
        import traceback
        trace_lines = traceback.format_exc().split('\n')
        for line in trace_lines:
            if line.strip():
                report_error(f"TRACE: {line}")
        return None
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                report_info(f"Cleaned up temp file: {temp_path}")
            except OSError as e:
                report_error(f"Warning: Could not delete temp file {temp_path}: {e}")


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


def capture_viewport_image(quality: int = 90) -> Optional[str]:
    """Capture the active viewport as base64 image"""
    temp_path = None
    try:
        # Create temporary file for saving the capture
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Save current render settings
        scene = bpy.context.scene
        render = scene.render
        
        original_filepath = render.filepath
        original_format = render.image_settings.file_format
        original_width = render.resolution_x
        original_height = render.resolution_y
        
        try:
            # Get dimensions from addon properties if available
            if hasattr(scene, 'runchat_properties'):
                render.resolution_x = scene.runchat_properties.viewport_width
                render.resolution_y = scene.runchat_properties.viewport_height
            else:
                # Default dimensions
                render.resolution_x = 1920
                render.resolution_y = 1080
            
            # Set capture settings
            render.filepath = temp_path
            render.image_settings.file_format = 'PNG'
            
            # Perform the capture using OpenGL render
            bpy.ops.render.opengl(write_still=True)
            
            # Convert to base64
            base64_data = image_to_base64(temp_path, quality)
            
            return base64_data
            
        finally:
            # Restore original settings
            render.filepath = original_filepath
            render.image_settings.file_format = original_format
            render.resolution_x = original_width
            render.resolution_y = original_height
            
    except Exception as e:
        print(f"Error capturing viewport: {e}")
        return None
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError as e:
                print(f"Warning: Could not delete temp file {temp_path}: {e}")


def setup_image_viewer(image_name: str) -> bool:
    """Setup an Image Editor area to show the specified image"""
    try:
        image = bpy.data.images.get(image_name)
        if not image:
            print(f"Image '{image_name}' not found in bpy.data.images")
            return False
        
        if not image.has_data:
            print(f"Image '{image_name}' has no data")
            return False
        
        print(f"Setting up Image Editor for '{image_name}' (size: {image.size[0]}x{image.size[1]})")
        
        # Method 1: Try to find an existing Image Editor
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                try:
                    area.spaces.active.image = image
                    area.tag_redraw()
                    print(f"Successfully set image in existing Image Editor")
                    return True
                except Exception as e:
                    print(f"Failed to set image in existing Image Editor: {e}")
                    continue
        
        print("No existing Image Editor found, attempting to convert an area...")
        
        # Method 2: Convert a suitable area to Image Editor
        # Prioritize areas that are less likely to be actively used
        conversion_candidates = ['TEXT_EDITOR', 'CONSOLE', 'INFO', 'OUTLINER', 'PROPERTIES']
        
        for area_type in conversion_candidates:
            for area in bpy.context.screen.areas:
                if area.type == area_type:
                    try:
                        old_type = area.type
                        area.type = 'IMAGE_EDITOR'
                        area.spaces.active.image = image
                        area.tag_redraw()
                        print(f"Successfully converted {old_type} to Image Editor")
                        return True
                    except Exception as e:
                        print(f"Failed to convert {area_type} to Image Editor: {e}")
                        continue
        
        print("Could not convert any existing area, attempting to split an area...")
        
        # Method 3: Try to split a large area
        largest_area = None
        largest_size = 0
        
        for area in bpy.context.screen.areas:
            area_size = area.width * area.height
            if area_size > largest_size and area.type in ['VIEW_3D', 'TEXT_EDITOR', 'CONSOLE']:
                largest_area = area
                largest_size = area_size
        
        if largest_area and largest_size > 200000:  # Only split if area is reasonably large
            try:
                # Split the area
                with bpy.context.temp_override(area=largest_area):
                    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
                
                # Find the new area and convert it
                for area in bpy.context.screen.areas:
                    if area != largest_area and area.type == largest_area.type:
                        area.type = 'IMAGE_EDITOR'
                        area.spaces.active.image = image
                        area.tag_redraw()
                        print(f"Successfully split area and created Image Editor")
                        return True
            except Exception as e:
                print(f"Failed to split area: {e}")
        
        # Method 4: Try to create a new window (last resort)
        try:
            bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
            print("Created new window, attempting to find Image Editor...")
            
            # Try to find and use any Image Editor in the new context
            for area in bpy.context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    try:
                        area.spaces.active.image = image
                        area.tag_redraw()
                        print("Successfully set image in new window Image Editor")
                        return True
                    except Exception as e:
                        print(f"Failed to set image in new window Image Editor: {e}")
            
            # If no Image Editor found, try to convert the last area
            if bpy.context.screen.areas:
                try:
                    last_area = bpy.context.screen.areas[-1]
                    last_area.type = 'IMAGE_EDITOR'
                    last_area.spaces.active.image = image
                    last_area.tag_redraw()
                    print("Converted new window area to Image Editor")
                    return True
                except Exception as e:
                    print(f"Failed to convert new window area: {e}")
                    
        except Exception as e:
            print(f"Failed to create new window: {e}")
        
        print("All methods failed to setup Image Editor")
        return False
        
    except Exception as e:
        print(f"Error setting up image viewer: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def auto_display_image(image_name: str) -> bool:
    """Automatically display an image using multiple methods"""
    try:
        # Method 1: Setup Image Editor
        if setup_image_viewer(image_name):
            return True
        
        # Method 2: Show in popup (fallback)
        try:
            bpy.ops.runchat.popup_image_viewer('INVOKE_DEFAULT', image_name=image_name)
            return True
        except:
            pass
        
        print(f"Could not auto-display image: {image_name}")
        return False
        
    except Exception as e:
        print(f"Error auto-displaying image: {e}")
        return False


def process_image_array(output_data, output_id, output_prop, runchat_props):
    """Process image output data that might be an array of images - simplified to use first image only"""
    try:
        if isinstance(output_data, list) and len(output_data) > 0:
            # Handle array of images - just take the first one
            print(f"Processing array of {len(output_data)} images for {output_id} - using first image only")
            first_image = output_data[0]
            
            if isinstance(first_image, str) and first_image.startswith('http'):
                # Set the value field so UI can display the URL
                output_prop.value = first_image
                output_prop.is_processed = True
                
                # Process just the first image
                process_single_image(first_image, output_id, output_prop)
            else:
                print(f"First image in array is not a valid URL: {first_image}")
        else:
            # Single image
            process_single_image(output_data, output_id, output_prop)
            
    except Exception as e:
        print(f"Error processing image array: {e}")
        import traceback
        print(traceback.format_exc())


def process_single_image(image_data, output_id, output_prop):
    """Process a single image (URL or base64)"""
    try:
        if isinstance(image_data, str):
            # Use Blender's Info log for debugging
            bpy.ops.info.reports_display_update()  # Refresh info area
            
            if image_data.startswith('http'):
                # Load image from URL
                image = load_image_from_url(image_data, output_prop.name)
            else:
                # Load image from base64
                image = load_image_from_base64(image_data, output_prop.name)
            
            if image:
                # Report success to Blender Info
                message = f"Successfully loaded image '{image.name}' with size {image.size[0]}x{image.size[1]}"
                bpy.context.window_manager.popup_menu(
                    lambda self, context: self.layout.label(text=message), 
                    title="Image Loaded", 
                    icon='INFO'
                )
                
                # Auto-display the image
                success = auto_display_image(image.name)
                if success:
                    print(f"Successfully displayed image: {image.name}")
                else:
                    print(f"Failed to display image: {image.name}")
            else:
                error_msg = f"Failed to load image for {output_id} (property: {output_prop.name})"
                bpy.context.window_manager.popup_menu(
                    lambda self, context: self.layout.label(text=error_msg), 
                    title="Image Load Error", 
                    icon='ERROR'
                )
                
    except Exception as e:
        error_msg = f"Error processing single image for {output_prop.name}: {e}"
        bpy.context.window_manager.popup_menu(
            lambda self, context: self.layout.label(text=error_msg), 
            title="Image Processing Error", 
            icon='ERROR'
        )
        import traceback
        print(traceback.format_exc()) 