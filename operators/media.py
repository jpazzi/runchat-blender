# operators/media.py

import bpy
import webbrowser
import os
import tempfile
import requests
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty

from .. import utils
from .. import preferences


class RUNCHAT_OT_view_image(Operator):
    """View output image"""
    bl_idname = "runchat.view_image"
    bl_label = "View Image"
    
    output_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.output_index < len(runchat_props.outputs):
            output_prop = runchat_props.outputs[self.output_index]
            if output_prop.value:
                try:
                    self.report({'INFO'}, "=== VIEW IMAGE DEBUG ===")
                    self.report({'INFO'}, f"Output property name: '{output_prop.name}'")
                    self.report({'INFO'}, f"Output property value: '{output_prop.value[:100]}...'")
                    
                    # Check if value is a URL or base64 data
                    if output_prop.value.startswith('http'):
                        self.report({'INFO'}, "Loading image from URL...")
                        # Load image from URL
                        image = utils.load_image_from_url(output_prop.value, output_prop.name, operator=self)
                    else:
                        self.report({'INFO'}, "Loading image from base64...")
                        # Load image data (assuming base64)
                        image = utils.load_image_from_base64(output_prop.value, output_prop.name)
                    
                    if image:
                        self.report({'INFO'}, f"Successfully loaded image: {image.name}")
                        self.report({'INFO'}, f"Image has data: {image.has_data}")
                        self.report({'INFO'}, f"Image size: {image.size[0]}x{image.size[1]}")
                        
                        # For single images, directly open in Image Editor
                        success = utils.setup_image_viewer(image.name)
                        if success:
                            self.report({'INFO'}, f"Opened {image.name} in Image Editor")
                        else:
                            # Fallback to popup if Image Editor setup fails
                            self.report({'WARNING'}, "Could not open Image Editor, showing popup instead")
                            bpy.ops.runchat.popup_image_viewer('INVOKE_DEFAULT', image_name=image.name)
                    else:
                        self.report({'ERROR'}, "Failed to load image - load_image_from_url returned None")
                        self.report({'ERROR'}, f"Attempted to load URL: {output_prop.value}")
                except Exception as e:
                    self.report({'ERROR'}, f"Exception in view_image: {e}")
                    import traceback
                    # Also log the traceback to Info
                    trace_lines = traceback.format_exc().split('\n')
                    for line in trace_lines:
                        if line.strip():
                            self.report({'ERROR'}, f"TRACE: {line}")
            else:
                self.report({'ERROR'}, "Output property has no value")
        else:
            self.report({'ERROR'}, f"Invalid output index: {self.output_index}")
        
        return {'FINISHED'}


class RUNCHAT_OT_save_image(Operator):
    """Save output image"""
    bl_idname = "runchat.save_image"
    bl_label = "Save Image"
    
    output_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.output_index < len(runchat_props.outputs):
            output_prop = runchat_props.outputs[self.output_index]
            if output_prop.value:
                try:
                    # Resolve and expand the save path
                    save_path = runchat_props.image_save_path
                    if save_path.startswith('//'):
                        # Blender relative path - convert to absolute
                        save_path = bpy.path.abspath(save_path)
                    elif save_path.startswith('~'):
                        # User home directory
                        save_path = os.path.expanduser(save_path)
                    
                    # Ensure the directory exists
                    os.makedirs(save_path, exist_ok=True)
                    
                    filename = f"{output_prop.name}.png"
                    full_path = os.path.join(save_path, filename)
                    
                    if output_prop.value.startswith('http'):
                        # Download and save image from URL
                        response = requests.get(output_prop.value, timeout=30)
                        response.raise_for_status()
                        
                        with open(full_path, 'wb') as f:
                            f.write(response.content)
                        
                        saved_path = full_path
                    else:
                        # Save base64 image data to disk
                        saved_path = utils.base64_to_image(output_prop.value, save_path, filename)
                    
                    if saved_path:
                        self.report({'INFO'}, f"Image saved to: {saved_path}")
                    else:
                        self.report({'ERROR'}, "Failed to save image")
                except Exception as e:
                    self.report({'ERROR'}, f"Error saving image: {e}")
        
        return {'FINISHED'}


class RUNCHAT_OT_open_image_editor(Operator):
    """Open image in Image Editor"""
    bl_idname = "runchat.open_image_editor"
    bl_label = "Open in Image Editor"
    
    image_name: StringProperty()
    
    def execute(self, context):
        try:
            self.report({'INFO'}, "=== OPEN IMAGE EDITOR DEBUG ===")
            self.report({'INFO'}, f"Requested image name: '{self.image_name}'")
            
            # List all available images in Blender
            self.report({'INFO'}, "Available images in bpy.data.images:")
            for img in bpy.data.images:
                size_info = f"{img.size[0]}x{img.size[1]}" if img.has_data else "N/A"
                self.report({'INFO'}, f"  - '{img.name}' (has_data: {img.has_data}, size: {size_info})")
            
            # Check if image exists
            image = bpy.data.images.get(self.image_name)
            if not image:
                self.report({'ERROR'}, f"Image '{self.image_name}' not found in Blender")
                return {'CANCELLED'}
            
            if not image.has_data:
                self.report({'ERROR'}, f"Image '{self.image_name}' has no data")
                return {'CANCELLED'}
            
            self.report({'INFO'}, f"Attempting to open '{self.image_name}' in Image Editor...")
            success = utils.setup_image_viewer(self.image_name)
            
            if success:
                self.report({'INFO'}, f"Successfully opened '{self.image_name}' in Image Editor")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Failed to setup Image Editor for '{self.image_name}'")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Exception in open_image_editor: {e}")
            import traceback
            # Also log the traceback to Info
            trace_lines = traceback.format_exc().split('\n')
            for line in trace_lines:
                if line.strip():
                    self.report({'ERROR'}, f"TRACE: {line}")
            return {'CANCELLED'}


class RUNCHAT_OT_save_image_as(Operator):
    """Save image with file browser"""
    bl_idname = "runchat.save_image_as"
    bl_label = "Save Image As"
    
    image_name: StringProperty()
    filepath: StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        try:
            image = bpy.data.images.get(self.image_name)
            if not image:
                self.report({'ERROR'}, f"Image '{self.image_name}' not found")
                return {'CANCELLED'}
            
            # Save the image
            image.save_render(self.filepath)
            self.report({'INFO'}, f"Image saved to: {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Error saving image: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if self.image_name:
            # Set default filename
            self.filepath = os.path.join(os.path.expanduser("~/Desktop"), f"{self.image_name}.png")
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class RUNCHAT_OT_popup_image_viewer(Operator):
    """Show image in popup window"""
    bl_idname = "runchat.popup_image_viewer"
    bl_label = "Image Viewer"
    
    image_name: StringProperty()
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)
    
    def draw(self, context):
        layout = self.layout
        
        image = bpy.data.images.get(self.image_name)
        if image:
            # Calculate display size while maintaining aspect ratio
            max_width = 550
            max_height = 400
            
            img_width = image.size[0] if image.size[0] > 0 else 512
            img_height = image.size[1] if image.size[1] > 0 else 512
            
            # Calculate scale to fit within max dimensions
            scale_w = max_width / img_width
            scale_h = max_height / img_height
            scale = min(scale_w, scale_h, 1.0)  # Don't scale up
            
            display_width = int(img_width * scale)
            display_height = int(img_height * scale)
            
            # Image info
            info_box = layout.box()
            info_box.label(text=f"Image: {self.image_name}")
            info_box.label(text=f"Size: {img_width} x {img_height}")
            info_box.label(text=f"Display: {display_width} x {display_height}")
            
            # Display the image
            layout.template_preview(image, show_buttons=False)
            
            # Action buttons
            button_row = layout.row()
            button_row.operator("runchat.open_image_editor", text="Open in Image Editor").image_name = self.image_name
            button_row.operator("runchat.save_image_as", text="Save As...").image_name = self.image_name
        else:
            layout.label(text=f"Image '{self.image_name}' not found", icon='ERROR')


class RUNCHAT_OT_open_video(Operator):
    """Open video in external player"""
    bl_idname = "runchat.open_video"
    bl_label = "Open Video"
    
    output_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.output_index < len(runchat_props.outputs):
            output_prop = runchat_props.outputs[self.output_index]
            if output_prop.value and output_prop.value.startswith('http'):
                try:
                    webbrowser.open(output_prop.value)
                    self.report({'INFO'}, f"Opening video: {output_prop.name}")
                except Exception as e:
                    self.report({'ERROR'}, f"Failed to open video: {e}")
            else:
                self.report({'ERROR'}, "No valid video URL")
        
        return {'FINISHED'}


class RUNCHAT_OT_save_video(Operator):
    """Save video file"""
    bl_idname = "runchat.save_video"
    bl_label = "Save Video"
    
    output_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.output_index < len(runchat_props.outputs):
            output_prop = runchat_props.outputs[self.output_index]
            if output_prop.value and output_prop.value.startswith('http'):
                try:
                    # Resolve and expand the save path
                    save_path = runchat_props.image_save_path  # Reuse image save path for videos
                    if save_path.startswith('//'):
                        # Blender relative path - convert to absolute
                        save_path = bpy.path.abspath(save_path)
                    elif save_path.startswith('~'):
                        # User home directory
                        save_path = os.path.expanduser(save_path)
                    
                    # Ensure the directory exists
                    os.makedirs(save_path, exist_ok=True)
                    
                    # Determine file extension from URL
                    url_lower = output_prop.value.lower()
                    if '.mp4' in url_lower:
                        ext = '.mp4'
                    elif '.mov' in url_lower:
                        ext = '.mov'
                    elif '.avi' in url_lower:
                        ext = '.avi'
                    elif '.mkv' in url_lower:
                        ext = '.mkv'
                    elif '.webm' in url_lower:
                        ext = '.webm'
                    else:
                        ext = '.mp4'  # Default
                    
                    filename = f"{output_prop.name}{ext}"
                    full_path = os.path.join(save_path, filename)
                    
                    # Download and save video
                    response = requests.get(output_prop.value, timeout=60)  # Longer timeout for videos
                    response.raise_for_status()
                    
                    with open(full_path, 'wb') as f:
                        f.write(response.content)
                    
                    self.report({'INFO'}, f"Video saved to: {full_path}")
                except Exception as e:
                    self.report({'ERROR'}, f"Error saving video: {e}")
            else:
                self.report({'ERROR'}, "No valid video URL")
        
        return {'FINISHED'}


class RUNCHAT_OT_import_model(Operator):
    """Import 3D model into Blender scene"""
    bl_idname = "runchat.import_model"
    bl_label = "Import Model"
    
    output_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.output_index >= len(runchat_props.outputs):
            self.report({'ERROR'}, "Invalid output index")
            return {'CANCELLED'}
        
        output_prop = runchat_props.outputs[self.output_index]
        
        if not output_prop.value or not output_prop.value.startswith('http'):
            self.report({'ERROR'}, "No valid model URL found")
            return {'CANCELLED'}
        
        try:
            # Download the model to a temporary file
            url = output_prop.value
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Determine file extension and format
            url_lower = url.lower()
            if '.gltf' in url_lower:
                ext = '.gltf'
                import_func = self.import_gltf
            elif '.glb' in url_lower:
                ext = '.glb'
                import_func = self.import_gltf  # Same importer for GLB
            elif '.obj' in url_lower:
                ext = '.obj'
                import_func = self.import_obj
            elif '.fbx' in url_lower:
                ext = '.fbx'
                import_func = self.import_fbx
            elif '.dae' in url_lower:
                ext = '.dae'
                import_func = self.import_dae
            elif '.blend' in url_lower:
                ext = '.blend'
                import_func = self.import_blend
            else:
                self.report({'ERROR'}, "Unsupported model format")
                return {'CANCELLED'}
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
                temp_file.write(response.content)
                temp_filepath = temp_file.name
            
            try:
                # Import the model
                import_func(temp_filepath)
                self.report({'INFO'}, f"Successfully imported {output_prop.name}")
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_filepath)
                except:
                    pass
                    
        except Exception as e:
            self.report({'ERROR'}, f"Error importing model: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def import_gltf(self, filepath):
        """Import GLTF/GLB file"""
        try:
            bpy.ops.import_scene.gltf(filepath=filepath)
        except:
            # Fallback for older Blender versions
            bpy.ops.import_scene.gltf2(filepath=filepath)
    
    def import_obj(self, filepath):
        """Import OBJ file"""
        bpy.ops.import_scene.obj(filepath=filepath)
    
    def import_fbx(self, filepath):
        """Import FBX file"""
        bpy.ops.import_scene.fbx(filepath=filepath)
    
    def import_dae(self, filepath):
        """Import DAE (Collada) file"""
        bpy.ops.wm.collada_import(filepath=filepath)
    
    def import_blend(self, filepath):
        """Import Blend file (append objects)"""
        # Append all objects from the blend file
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = data_from.objects
        
        # Link objects to current scene
        for obj in data_to.objects:
            if obj:
                bpy.context.collection.objects.link(obj)


class RUNCHAT_OT_save_model(Operator):
    """Save 3D model to file"""
    bl_idname = "runchat.save_model"
    bl_label = "Save Model"
    
    output_index: IntProperty()
    filepath: StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.output_index >= len(runchat_props.outputs):
            self.report({'ERROR'}, "Invalid output index")
            return {'CANCELLED'}
        
        output_prop = runchat_props.outputs[self.output_index]
        
        if not output_prop.value:
            self.report({'ERROR'}, "No model data available")
            return {'CANCELLED'}
        
        try:
            # Handle URL-based models
            if output_prop.value.startswith('http'):
                # Download the model
                response = requests.get(output_prop.value, timeout=30)
                response.raise_for_status()
                model_data = response.content
                
                # Determine extension from URL
                url_lower = output_prop.value.lower()
                if '.gltf' in url_lower:
                    ext = '.gltf'
                elif '.glb' in url_lower:
                    ext = '.glb'
                elif '.obj' in url_lower:
                    ext = '.obj'
                elif '.fbx' in url_lower:
                    ext = '.fbx'
                elif '.dae' in url_lower:
                    ext = '.dae'
                elif '.blend' in url_lower:
                    ext = '.blend'
                else:
                    ext = '.gltf'  # Default
                    
            else:
                # Handle base64 encoded data (legacy)
                import base64
                model_data = base64.b64decode(output_prop.value)
                ext = '.gltf'  # Default for base64
            
            # Generate filename if not provided
            if not self.filepath:
                output_dir = bpy.path.abspath(runchat_props.image_save_path)
                os.makedirs(output_dir, exist_ok=True)
                self.filepath = os.path.join(output_dir, f"{output_prop.name}{ext}")
            
            # Write to file
            with open(self.filepath, 'wb') as f:
                f.write(model_data)
            
            self.report({'INFO'}, f"Model saved to {self.filepath}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error saving model: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.output_index < len(runchat_props.outputs):
            output_prop = runchat_props.outputs[self.output_index]
            
            # Determine extension from URL if possible
            if output_prop.value and output_prop.value.startswith('http'):
                url_lower = output_prop.value.lower()
                if '.gltf' in url_lower:
                    ext = '.gltf'
                elif '.glb' in url_lower:
                    ext = '.glb'
                elif '.obj' in url_lower:
                    ext = '.obj'
                elif '.fbx' in url_lower:
                    ext = '.fbx'
                elif '.dae' in url_lower:
                    ext = '.dae'
                elif '.blend' in url_lower:
                    ext = '.blend'
                else:
                    ext = '.gltf'
            else:
                ext = '.gltf'
            
            self.filepath = f"{output_prop.name}{ext}"
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# Classes to register
classes = [
    RUNCHAT_OT_view_image,
    RUNCHAT_OT_save_image,
    RUNCHAT_OT_open_image_editor,
    RUNCHAT_OT_save_image_as,
    RUNCHAT_OT_popup_image_viewer,
    RUNCHAT_OT_open_video,
    RUNCHAT_OT_save_video,
    RUNCHAT_OT_import_model,
    RUNCHAT_OT_save_model,
] 