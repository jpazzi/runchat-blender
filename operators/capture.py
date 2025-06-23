# operators/capture.py

import bpy
from bpy.types import Operator
from bpy.props import IntProperty

from .. import api
from .. import preferences
from .. import utils


class RUNCHAT_OT_preview_viewport(Operator):
    """Preview viewport capture"""
    bl_idname = "runchat.preview_viewport"
    bl_label = "Preview Viewport"
    
    input_index: IntProperty()
    
    def execute(self, context):
        try:
            scene = context.scene
            runchat_props = scene.runchat_properties
            
            # Store original render settings
            render = scene.render
            original_resolution_x = render.resolution_x
            original_resolution_y = render.resolution_y
            original_percentage = render.resolution_percentage
            
            # Set custom viewport capture dimensions
            render.resolution_x = runchat_props.viewport_width
            render.resolution_y = runchat_props.viewport_height
            render.resolution_percentage = 100
            
            print(f"Previewing viewport at {runchat_props.viewport_width}x{runchat_props.viewport_height}")
            
            # Capture viewport
            image_data = utils.capture_viewport_image(quality=runchat_props.viewport_quality)
            
            # Restore original render settings
            render.resolution_x = original_resolution_x
            render.resolution_y = original_resolution_y
            render.resolution_percentage = original_percentage
            
            if image_data:
                # Load image into Blender for preview
                image = utils.load_image_from_base64(image_data, "Viewport_Preview")
                
                if image:
                    # Try to show in image editor
                    for area in context.screen.areas:
                        if area.type == 'IMAGE_EDITOR':
                            area.spaces.active.image = image
                            break
                    
                    self.report({'INFO'}, f"Viewport captured successfully at {runchat_props.viewport_width}x{runchat_props.viewport_height}")
                else:
                    self.report({'ERROR'}, "Failed to load viewport image")
                    return {'CANCELLED'}
            else:
                self.report({'ERROR'}, "Failed to capture viewport")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error capturing viewport: {str(e)}")
            print(f"Preview viewport error: {e}")
            import traceback
            print(traceback.format_exc())
            return {'CANCELLED'}
        
        return {'FINISHED'}


class RUNCHAT_OT_upload_viewport(Operator):
    """Capture viewport and upload to RunChat"""
    bl_idname = "runchat.upload_viewport"
    bl_label = "Upload Viewport"
    
    input_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.input_index >= len(runchat_props.inputs):
            self.report({'ERROR'}, "Invalid input index")
            return {'CANCELLED'}
        
        input_prop = runchat_props.inputs[self.input_index]
        
        # Get API key
        api_key = preferences.get_api_key()
        if not api_key:
            self.report({'ERROR'}, "Please set your RunChat API key in addon preferences")
            return {'CANCELLED'}
        
        try:
            # Update status
            input_prop.upload_status = "Capturing viewport..."
            
            # Capture viewport
            image_data = self.capture_viewport(context)
            if not image_data:
                input_prop.upload_status = "Failed to capture viewport"
                self.report({'ERROR'}, "Failed to capture viewport")
                return {'CANCELLED'}
            
            # Upload to RunChat
            input_prop.upload_status = "Uploading to RunChat..."
            filename = f"viewport_capture_{input_prop.param_id}.png"
            
            uploaded_url = api.RunChatAPI.upload_image(image_data, filename, api_key)
            
            if uploaded_url:
                input_prop.uploaded_url = uploaded_url
                input_prop.text_value = uploaded_url  # Also set as text value for execution
                input_prop.upload_status = "Upload successful!"
                self.report({'INFO'}, f"Viewport uploaded successfully: {uploaded_url}")
            else:
                input_prop.upload_status = "Upload failed"
                self.report({'ERROR'}, "Failed to upload image to RunChat")
                return {'CANCELLED'}
                
        except Exception as e:
            input_prop.upload_status = f"Error: {str(e)}"
            self.report({'ERROR'}, f"Error uploading viewport: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def capture_viewport(self, context):
        """Capture the current viewport as base64 image with custom dimensions"""
        try:
            scene = context.scene
            runchat_props = scene.runchat_properties
            
            # Store original render settings
            render = scene.render
            original_resolution_x = render.resolution_x
            original_resolution_y = render.resolution_y
            original_percentage = render.resolution_percentage
            
            # Set custom viewport capture dimensions
            render.resolution_x = runchat_props.viewport_width
            render.resolution_y = runchat_props.viewport_height
            render.resolution_percentage = 100
            
            print(f"Capturing viewport at {runchat_props.viewport_width}x{runchat_props.viewport_height}")
            
            # Use the proper viewport capture function from utils
            base64_data = utils.capture_viewport_image(quality=runchat_props.viewport_quality)
            
            # Restore original render settings
            render.resolution_x = original_resolution_x
            render.resolution_y = original_resolution_y
            render.resolution_percentage = original_percentage
            
            if base64_data:
                print("Viewport captured successfully")
                return base64_data
            else:
                print("Failed to capture viewport - no data returned")
                return None
            
        except Exception as e:
            print(f"Error capturing viewport: {e}")
            import traceback
            print(traceback.format_exc())
            return None


class RUNCHAT_OT_preview_image(Operator):
    """Preview input image"""
    bl_idname = "runchat.preview_image"
    bl_label = "Preview Image"
    
    input_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.input_index < len(runchat_props.inputs):
            input_prop = runchat_props.inputs[self.input_index]
            
            if input_prop.use_viewport_capture:
                # Capture and preview viewport
                image_data = self.capture_viewport(context)
                if image_data:
                    image = utils.load_image_from_base64(image_data, f"Preview_{input_prop.name}")
                    if image:
                        utils.setup_image_viewer(image.name)
                        self.report({'INFO'}, f"Viewport captured and loaded: {image.name}")
                    else:
                        self.report({'ERROR'}, "Failed to load captured image")
                else:
                    self.report({'ERROR'}, "Failed to capture viewport")
            
            elif input_prop.file_path:
                # Load and preview file
                try:
                    image = bpy.data.images.load(input_prop.file_path)
                    image.name = f"Preview_{input_prop.name}"
                    utils.setup_image_viewer(image.name)
                    self.report({'INFO'}, f"Image loaded: {image.name}")
                except Exception as e:
                    self.report({'ERROR'}, f"Failed to load image: {e}")
            
            else:
                self.report({'WARNING'}, "No image source configured")
        
        return {'FINISHED'}
    
    def capture_viewport(self, context):
        """Capture current viewport as image"""
        try:
            scene = context.scene
            runchat_props = scene.runchat_properties
            
            # Store original render settings
            render = scene.render
            original_resolution_x = render.resolution_x
            original_resolution_y = render.resolution_y
            original_percentage = render.resolution_percentage
            
            # Set custom viewport capture dimensions
            render.resolution_x = runchat_props.viewport_width
            render.resolution_y = runchat_props.viewport_height
            render.resolution_percentage = 100
            
            # Use the proper viewport capture function from utils
            base64_data = utils.capture_viewport_image(quality=runchat_props.viewport_quality)
            
            # Restore original render settings
            render.resolution_x = original_resolution_x
            render.resolution_y = original_resolution_y
            render.resolution_percentage = original_percentage
            
            return base64_data
            
        except Exception as e:
            print(f"Error capturing viewport: {e}")
            return None


classes = [
    RUNCHAT_OT_preview_viewport,
    RUNCHAT_OT_upload_viewport,
    RUNCHAT_OT_preview_image,
] 