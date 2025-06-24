# operators/media.py

import bpy
import webbrowser
import os
import tempfile
import requests
import time
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
        if image and image.has_data:
            # Calculate image display size
            max_width = 500
            max_height = 400
            
            img_width, img_height = image.size
            if img_width > max_width or img_height > max_height:
                scale = min(max_width / img_width, max_height / img_height)
                display_width = int(img_width * scale)
                display_height = int(img_height * scale)
            else:
                display_width = img_width
                display_height = img_height
            
            # Image preview
            layout.template_preview(image)
            
            # Image info
            row = layout.row()
            row.label(text=f"Size: {img_width} x {img_height}")
            
            # Action buttons
            row = layout.row()
            op = row.operator("runchat.open_image_editor", text="Open in Image Editor")
            op.image_name = self.image_name
            
            op = row.operator("runchat.save_image_as", text="Save As...")
            op.image_name = self.image_name
        else:
            layout.label(text="Image not found or has no data")


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
            if output_prop.value:
                try:
                    webbrowser.open(output_prop.value)
                    self.report({'INFO'}, f"Opened video '{output_prop.name}' in external player")
                except Exception as e:
                    self.report({'ERROR'}, f"Error opening video: {e}")
        
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
            if output_prop.value:
                try:
                    # Download video
                    response = requests.get(output_prop.value, timeout=60)
                    response.raise_for_status()
                    
                    # Determine file extension
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
                    
                    # Resolve and expand the save path
                    save_path = runchat_props.video_save_path
                    if save_path.startswith('//'):
                        # Blender relative path - convert to absolute
                        save_path = bpy.path.abspath(save_path)
                    elif save_path.startswith('~'):
                        # User home directory
                        save_path = os.path.expanduser(save_path)
                    
                    # Ensure the directory exists
                    os.makedirs(save_path, exist_ok=True)
                    
                    filename = f"{output_prop.name}{ext}"
                    full_path = os.path.join(save_path, filename)
                    
                    with open(full_path, 'wb') as f:
                        f.write(response.content)
                    
                    self.report({'INFO'}, f"Video saved to: {full_path}")
                except Exception as e:
                    self.report({'ERROR'}, f"Error saving video: {e}")
        
        return {'FINISHED'}


def force_video_sequencer_interface():
    """Force the Video Sequencer interface by opening a new window"""
    print("=== OPENING NEW VIDEO SEQUENCER WINDOW ===")
    
    try:
        # Open a new window
        bpy.ops.wm.window_new()
        
        # Get the new window
        new_window = bpy.context.window_manager.windows[-1]
        
        # Set the new window to use Video Editing workspace if available
        video_workspace = None
        for workspace in bpy.data.workspaces:
            if 'Video Editing' in workspace.name:
                video_workspace = workspace
                break
        
        if video_workspace:
            print(f"Setting new window to Video Editing workspace: {video_workspace.name}")
            new_window.workspace = video_workspace
        
        # Get the screen from the new window
        screen = new_window.screen
        
        # Find the largest area in the new window and convert it to Video Sequencer
        largest_area = None
        largest_size = 0
        
        for area in screen.areas:
            area_size = area.width * area.height
            if area_size > largest_size:
                largest_area = area
                largest_size = area_size
        
        if largest_area:
            print(f"Converting area in new window to SEQUENCE_EDITOR")
            print(f"Area size: {largest_area.width}x{largest_area.height}")
            
            # Change to sequence editor
            largest_area.type = 'SEQUENCE_EDITOR'
            
            # Set to sequencer+preview mode with small delay
            bpy.app.timers.register(lambda: set_sequencer_mode_in_window(largest_area), first_interval=0.1)
            
            print("Successfully opened new Video Sequencer window")
            return "Opened new Video Sequencer window"
        else:
            print("Could not find suitable area in new window")
            return "Opened new window but could not configure Video Sequencer"
            
    except Exception as e:
        print(f"Error opening new window: {e}")
        # Fallback to original approach
        return force_video_sequencer_interface_fallback()


def set_sequencer_mode_in_window(area):
    """Set the sequencer to preview mode in the new window"""
    if area and area.type == 'SEQUENCE_EDITOR':
        for space in area.spaces:
            if space.type == 'SEQUENCE_EDITOR':
                print("Setting sequencer in new window to SEQUENCER_PREVIEW mode")
                space.view_type = 'SEQUENCER_PREVIEW'
                break
        area.tag_redraw()
    return None  # Don't repeat timer


def force_video_sequencer_interface_fallback():
    """Fallback method - convert existing area"""
    print("=== FALLBACK: FORCING VIDEO SEQUENCER INTERFACE ===")
    
    # Find the largest area that's not essential (avoid Properties, Outliner, Console)
    largest_area = None
    largest_size = 0
    
    for area in bpy.context.screen.areas:
        area_size = area.width * area.height
        # Skip essential areas and small areas
        if (area.type not in ['PROPERTIES', 'OUTLINER', 'FILE_BROWSER', 'INFO'] 
            and area_size > largest_size 
            and area_size > 10000):  # Ensure it's big enough
            largest_area = area
            largest_size = area_size
    
    if largest_area:
        original_type = largest_area.type
        print(f"Converting largest area ({original_type}) to SEQUENCE_EDITOR")
        print(f"Area size: {largest_area.width}x{largest_area.height}")
        
        # Change to sequence editor
        largest_area.type = 'SEQUENCE_EDITOR'
        
        # Set to sequencer+preview mode with small delay
        bpy.app.timers.register(lambda: set_sequencer_mode(largest_area), first_interval=0.1)
        
        print(f"Successfully converted {original_type} area to Video Sequencer")
        return f"Opened Video Sequencer (converted from {original_type})"
    else:
        print("Could not find suitable area to convert to Video Sequencer")
        return "Could not open Video Sequencer interface"


def set_sequencer_mode(area):
    """Set the sequencer to preview mode - called with a timer to ensure it takes effect"""
    if area and area.type == 'SEQUENCE_EDITOR':
        for space in area.spaces:
            if space.type == 'SEQUENCE_EDITOR':
                print("Setting sequencer to SEQUENCER_PREVIEW mode")
                space.view_type = 'SEQUENCER_PREVIEW'
                break
        area.tag_redraw()
        # Force screen update
        bpy.context.view_layer.update()
    return None  # Don't repeat timer


class RUNCHAT_OT_import_model(Operator):
    """Import 3D model into Blender scene"""
    bl_idname = "runchat.import_model"
    bl_label = "Import Model"
    
    output_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.output_index < len(runchat_props.outputs):
            output_prop = runchat_props.outputs[self.output_index]
            if output_prop.value:
                try:
                    # Download model file
                    response = requests.get(output_prop.value, timeout=60)
                    response.raise_for_status()
                    
                    # Determine file extension
                    url_lower = output_prop.value.lower()
                    if '.gltf' in url_lower or '.glb' in url_lower:
                        ext = '.gltf' if '.gltf' in url_lower else '.glb'
                        import_func = self.import_gltf
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
                        self.report({'ERROR'}, f"Unsupported model format: {output_prop.value}")
                        return {'CANCELLED'}
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
                        temp_file.write(response.content)
                        temp_filepath = temp_file.name
                    
                    try:
                        # Import the model
                        import_func(temp_filepath)
                        self.report({'INFO'}, f"Successfully imported model '{output_prop.name}'")
                    finally:
                        # Clean up
                        os.unlink(temp_filepath)
                        
                except Exception as e:
                    self.report({'ERROR'}, f"Error importing model: {e}")
                    return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def import_gltf(self, filepath):
        bpy.ops.import_scene.gltf(filepath=filepath)
    
    def import_obj(self, filepath):
        bpy.ops.import_scene.obj(filepath=filepath)
    
    def import_fbx(self, filepath):
        bpy.ops.import_scene.fbx(filepath=filepath)
    
    def import_dae(self, filepath):
        bpy.ops.wm.collada_import(filepath=filepath)
    
    def import_blend(self, filepath):
        # For .blend files, we append objects from the file
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = data_from.objects
        
        # Link objects to current scene
        for obj in data_to.objects:
            if obj is not None:
                bpy.context.collection.objects.link(obj)


class RUNCHAT_OT_save_model(Operator):
    """Save 3D model to file"""
    bl_idname = "runchat.save_model"
    bl_label = "Save Model"
    
    output_index: IntProperty()
    filepath: StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        try:
            # Get selected objects or all objects if none selected
            selected_objects = bpy.context.selected_objects
            if not selected_objects:
                # Select all mesh objects
                for obj in bpy.context.scene.objects:
                    if obj.type == 'MESH':
                        obj.select_set(True)
                selected_objects = bpy.context.selected_objects
            
            if not selected_objects:
                self.report({'ERROR'}, "No objects to export")
                return {'CANCELLED'}
            
            # Determine export format from filepath extension
            filepath_lower = self.filepath.lower()
            if filepath_lower.endswith('.gltf'):
                bpy.ops.export_scene.gltf(filepath=self.filepath, use_selection=True)
            elif filepath_lower.endswith('.glb'):
                bpy.ops.export_scene.gltf(filepath=self.filepath, use_selection=True, export_format='GLB')
            elif filepath_lower.endswith('.obj'):
                bpy.ops.export_scene.obj(filepath=self.filepath, use_selection=True)
            elif filepath_lower.endswith('.fbx'):
                bpy.ops.export_scene.fbx(filepath=self.filepath, use_selection=True)
            elif filepath_lower.endswith('.dae'):
                bpy.ops.wm.collada_export(filepath=self.filepath, selected=True)
            elif filepath_lower.endswith('.blend'):
                # For .blend, save a new blend file
                bpy.ops.wm.save_as_mainfile(filepath=self.filepath, copy=True)
            else:
                self.report({'ERROR'}, "Unsupported export format")
                return {'CANCELLED'}
            
            self.report({'INFO'}, f"Model saved to: {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Error saving model: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class RUNCHAT_OT_import_video(Operator):
    """Import video into Video Sequencer"""
    bl_idname = "runchat.import_video"
    bl_label = "Import to Video Sequencer"
    
    output_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.output_index >= len(runchat_props.outputs):
            self.report({'ERROR'}, f"Invalid output index: {self.output_index}")
            return {'CANCELLED'}
        
        output_prop = runchat_props.outputs[self.output_index]
        if not output_prop.value:
            self.report({'ERROR'}, "Output property has no value")
            return {'CANCELLED'}
        
        print("=== VIDEO IMPORT DEBUG START ===")
        self.report({'INFO'}, f"Importing video: {output_prop.name}")
        
        try:
            # Download the video to a temporary file
            print(f"Downloading video from: {output_prop.value}")
            self.report({'INFO'}, "Downloading video...")
            
            response = requests.get(output_prop.value, timeout=60)
            response.raise_for_status()
            print(f"Video downloaded successfully. Size: {len(response.content)} bytes")
            
            # Determine file extension
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
            elif '.m4v' in url_lower:
                ext = '.m4v'
            else:
                ext = '.mp4'  # Default
            
            print(f"Detected video format: {ext}")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
                temp_file.write(response.content)
                temp_filepath = temp_file.name
            
            print(f"Video saved to temporary file: {temp_filepath}")
            
            # Copy to a more permanent location in user's temp directory
            import shutil
            permanent_filename = f"runchat_video_{output_prop.name}_{int(time.time())}{ext}"
            permanent_filepath = os.path.join(tempfile.gettempdir(), permanent_filename)
            shutil.copy2(temp_filepath, permanent_filepath)
            print(f"Video copied to permanent location: {permanent_filepath}")
            
            try:
                # Force Video Sequencer interface FIRST
                status_message = force_video_sequencer_interface()
                
                # Ensure we have a Video Sequencer scene setup
                print(f"Scene has sequence editor: {scene.sequence_editor is not None}")
                if not scene.sequence_editor:
                    print("Creating sequence editor...")
                    scene.sequence_editor_create()
                    self.report({'INFO'}, "Created Video Sequencer for scene")
                
                # Find or use the sequence editor area
                sequencer_area = None
                for area in bpy.context.screen.areas:
                    if area.type == 'SEQUENCE_EDITOR':
                        sequencer_area = area
                        break
                
                if not sequencer_area:
                    raise Exception("Could not find Sequence Editor area after forcing interface")
                
                print(f"Using sequence editor area: {sequencer_area}")
                
                # Get the space data for proper context
                sequencer_space = None
                for space in sequencer_area.spaces:
                    if space.type == 'SEQUENCE_EDITOR':
                        sequencer_space = space
                        break
                
                # Set the context and import the video
                with bpy.context.temp_override(area=sequencer_area, space_data=sequencer_space):
                    # Import the video into the sequencer
                    print("Adding movie strip to sequencer...")
                    bpy.ops.sequencer.movie_strip_add(
                        filepath=permanent_filepath,
                        frame_start=1,
                        channel=1
                    )
                    print("Movie strip added successfully")
                
                # Set the scene frame range to match the video
                if scene.sequence_editor.sequences:
                    last_sequence = scene.sequence_editor.sequences[-1]
                    print(f"Video sequence length: {last_sequence.frame_final_end} frames")
                    scene.frame_end = last_sequence.frame_final_end
                    self.report({'INFO'}, f"Set scene length to {last_sequence.frame_final_end} frames")
                
                success_msg = f"Successfully imported video '{output_prop.name}' to Video Sequencer"
                print(success_msg)
                self.report({'INFO'}, success_msg)
                self.report({'INFO'}, status_message)
                self.report({'INFO'}, f"Video file location: {permanent_filepath}")
                
            finally:
                # Clean up only the temporary file, keep the permanent one
                try:
                    os.unlink(temp_filepath)
                    print(f"Cleaned up temporary file: {temp_filepath}")
                    print(f"Permanent video file kept at: {permanent_filepath}")
                except Exception as cleanup_error:
                    print(f"Failed to cleanup temp file: {cleanup_error}")
                    
        except Exception as e:
            error_msg = f"Error importing video: {e}"
            print(error_msg)
            print(f"Full exception: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}
        
        print("=== VIDEO IMPORT DEBUG END ===")
        return {'FINISHED'}


class RUNCHAT_OT_open_video_editor(Operator):
    """Open Video Editor workspace"""
    bl_idname = "runchat.open_video_editor"
    bl_label = "Open Video Editor"
    
    def execute(self, context):
        try:
            print("=== OPENING VIDEO EDITOR WORKSPACE ===")
            self.report({'INFO'}, "Opening Video Editor workspace...")
            
            status_message = force_video_sequencer_interface()
            
            # Ensure we have a Video Sequencer scene setup
            scene = context.scene
            if not scene.sequence_editor:
                print("Creating sequence editor...")
                scene.sequence_editor_create()
                self.report({'INFO'}, "Created Video Sequencer for scene")
            
            self.report({'INFO'}, status_message)
            print("Video Editor opened successfully")
                
        except Exception as e:
            error_msg = f"Error opening Video Editor: {e}"
            print(error_msg)
            self.report({'ERROR'}, error_msg)
            
        return {'FINISHED'}


# Classes to register
classes = [
    RUNCHAT_OT_view_image,
    RUNCHAT_OT_save_image,
    RUNCHAT_OT_open_image_editor,
    RUNCHAT_OT_save_image_as,
    RUNCHAT_OT_popup_image_viewer,
    RUNCHAT_OT_open_video_editor,
    RUNCHAT_OT_open_video,
    RUNCHAT_OT_save_video,
    RUNCHAT_OT_import_model,
    RUNCHAT_OT_save_model,
    RUNCHAT_OT_import_video,
] 