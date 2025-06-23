# ui/panels.py

import bpy
from bpy.types import Panel

from . import helpers


class RUNCHAT_PT_main_panel(Panel):
    bl_label = "Runchat Workflow"
    bl_idname = "RUNCHAT_PT_main_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Main controls
        row = layout.row()
        row.prop(runchat_props, "runchat_id")
        row.operator("runchat.load_schema", text="", icon="IMPORT")
            
        # Workflow info
        if runchat_props.schema_loaded:
            box = layout.box()
            box.label(text=f"Workflow: {runchat_props.workflow_name}", icon="FILE_SCRIPT")
            
            # Open in Editor button (only show when schema is loaded)
            if runchat_props.runchat_id:
                editor_row = box.row()
                editor_row.operator("runchat.open_editor", text="Open in Editor", icon="URL")
            
            # Status and progress
            if runchat_props.status != "Ready":
                box.label(text=f"Status: {runchat_props.status}")
                if runchat_props.progress > 0:
                    box.prop(runchat_props, "progress", slider=True)
                    if runchat_props.progress_message:
                        box.label(text=runchat_props.progress_message)



class RUNCHAT_PT_inputs_panel(Panel):
    bl_label = "Inputs"
    bl_idname = "RUNCHAT_PT_inputs_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "RUNCHAT_PT_main_panel"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        return runchat_props.schema_loaded and len(runchat_props.inputs) > 0
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Inputs section
        for i, input_prop in enumerate(runchat_props.inputs):
            self.draw_input_property(layout, input_prop, i, context)

    def draw_input_property(self, layout, input_prop, index, context):
        """Draw an input property with all its controls"""
        box = layout.box()
        
        # Header with name only (remove type display)
        header = box.row()
        header.label(text=input_prop.name, icon="IMPORT")
        
        # Description - multiline support with markdown links
        if input_prop.description:
            desc_box = box.box()
            desc_box.scale_y = 0.8
            
            # Split description into lines and display each
            desc_lines = input_prop.description.split('\n')
            for line in desc_lines:
                helpers.draw_description_line(desc_box, line, context)
        
        # Simple text input
        text_row = box.row()
        text_row.prop(input_prop, "text_value", text="Text Input")
        
        # Show uploaded URL if available
        if input_prop.uploaded_url:
            url_box = box.box()
            url_box.scale_y = 0.8
            url_box.label(text=f"Uploaded: {input_prop.uploaded_url[:60]}{'...' if len(input_prop.uploaded_url) > 60 else ''}", icon="CHECKMARK")
        
        # Image upload section (expandable for all text inputs)
        upload_box = box.box()
        upload_header = upload_box.row()
        upload_header.prop(input_prop, "use_viewport_capture", 
                          text="Upload Image Instead", 
                          icon="TRIA_DOWN" if input_prop.use_viewport_capture else "TRIA_RIGHT",
                          emboss=False)
        
        if input_prop.use_viewport_capture:
            # Upload options when expanded
            upload_content = upload_box.box()
            upload_content.label(text="Choose upload method:", icon="IMAGE_DATA")
            
            # Viewport capture option
            viewport_section = upload_content.box()
            viewport_section.label(text="Viewport Capture:", icon="CAMERA_DATA")
            viewport_row = viewport_section.row()
            viewport_row.operator("runchat.upload_viewport", text="Capture & Upload Viewport", icon="CAMERA_DATA").input_index = index
            preview_row = viewport_section.row()
            preview_row.operator("runchat.preview_viewport", text="Preview Viewport Only", icon="HIDE_OFF").input_index = index
            
            # File upload option
            file_section = upload_content.box()
            file_section.label(text="File Upload:", icon="FILE_FOLDER")
            file_row = file_section.row()
            file_row.prop(input_prop, "file_path", text="")
            
            if input_prop.file_path:
                upload_row = file_section.row()
                upload_row.operator("runchat.upload_file", text="Upload Selected File", icon="EXPORT").input_index = index
                preview_row = file_section.row()
                preview_row.operator("runchat.preview_image", text="Preview File", icon="FILE_IMAGE").input_index = index
            
            # Upload status
            if input_prop.upload_status:
                status_row = upload_content.row()
                if "success" in input_prop.upload_status.lower():
                    status_row.label(text=input_prop.upload_status, icon="CHECKMARK")
                elif "error" in input_prop.upload_status.lower():
                    status_row.label(text=input_prop.upload_status, icon="ERROR")
                else:
                    status_row.label(text=input_prop.upload_status, icon="TIME")


class RUNCHAT_PT_outputs_panel(Panel):
    bl_label = "Outputs"
    bl_idname = "RUNCHAT_PT_outputs_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "RUNCHAT_PT_main_panel"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        return runchat_props.schema_loaded and len(runchat_props.outputs) > 0
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Outputs section
        for i, output_prop in enumerate(runchat_props.outputs):
            self.draw_output_property(layout, output_prop, i, context)

    def draw_output_property(self, layout, output_prop, index, context):
        """Draw an output property with its controls"""
        box = layout.box()
        
        # Header with name only (remove type display)
        header = box.row()
        header.label(text=output_prop.name, icon="EXPORT")
        
        # Check if execution is in progress
        scene = bpy.context.scene
        runchat_props = scene.runchat_properties
        is_executing = ("Executing" in runchat_props.status or 
                       "processing" in runchat_props.status.lower() or
                       "Starting" in runchat_props.status or
                       (runchat_props.progress > 0.0 and runchat_props.progress < 1.0))
        
        # Show running status if execution is in progress
        if is_executing and not output_prop.value:
            status_box = box.box()
            status_box.alert = True  # Make it stand out with alert styling
            
            status_row = status_box.row()
            status_row.alignment = 'CENTER'
            status_row.label(text="⏳ Generating output...", icon="TIME")
            
            # Show progress bar if available
            if runchat_props.progress > 0.0:
                progress_box = status_box.box()
                progress_row = progress_box.row()
                progress_row.prop(runchat_props, "progress", text="Progress", slider=True)
                
                # Show percentage
                percentage = int(runchat_props.progress * 100)
                progress_row.label(text=f"{percentage}%")
            
            # Show progress message if available
            if runchat_props.progress_message and runchat_props.progress_message != "Initializing...":
                msg_row = status_box.row()
                msg_row.alignment = 'CENTER'
                msg_row.label(text=runchat_props.progress_message, icon="INFO")
            
            # Add a subtle animation hint
            hint_row = status_box.row()
            hint_row.alignment = 'CENTER'
            hint_row.scale_y = 0.8
            hint_row.label(text="Please wait while Runchat processes your request", icon="NONE")
                
        # Output controls based on type
        elif output_prop.value:
            if output_prop.output_type == "image":
                # Show image preview directly in the panel
                self.draw_image_output(box, output_prop, index)
            elif output_prop.output_type == "video":
                # Show video output controls
                self.draw_video_output(box, output_prop, index)
            elif output_prop.output_type == "model":
                # Show 3D model output controls
                self.draw_model_output(box, output_prop, index)
            elif output_prop.output_type == "text":
                # Show text output in multiline format
                text_box = box.box()
                text_box.label(text="Output:")
                helpers.format_text_output(text_box, output_prop.value, context=context)
                controls_row = box.row()
                controls_row.operator("runchat.copy_text", text="Copy", icon="COPYDOWN").output_index = index
            else:
                # Generic output
                controls_row = box.row()
                controls_row.operator("runchat.copy_text", text="Copy", icon="COPYDOWN").output_index = index
        else:
            box.label(text="No output yet", icon="X")
    
    def draw_image_output(self, layout, output_prop, index):
        """Draw image output with inline preview"""
        # Try to get the loaded image
        image_name = output_prop.name
        image = bpy.data.images.get(image_name)
        
        if image and image.has_data:
            # Show image preview
            preview_box = layout.box()
            preview_box.label(text=f"Size: {image.size[0]} x {image.size[1]}", icon="INFO")
            
            # Image preview with reasonable size
            col = preview_box.column()
            col.scale_y = 3.0  # Make preview taller
            col.template_preview(image, show_buttons=False)
            
            # Action buttons
            controls_row = preview_box.row()
            controls_row.operator("runchat.open_image_editor", text="Open in Editor", icon="IMAGE_DATA").image_name = image_name
            controls_row.operator("runchat.save_image", text="Save", icon="FILE_FOLDER").output_index = index
        else:
            # Image not loaded yet, show URL and load button
            url_box = layout.box()
            url_preview = output_prop.value[:50] + "..." if len(output_prop.value) > 50 else output_prop.value
            url_box.label(text=f"URL: {url_preview}", icon="URL")
            
            controls_row = url_box.row()
            controls_row.operator("runchat.view_image", text="Open in Image Editor", icon="IMAGE_DATA").output_index = index
            controls_row.operator("runchat.save_image", text="Save", icon="FILE_FOLDER").output_index = index
    
    def draw_video_output(self, layout, output_prop, index):
        """Draw video output with controls"""
        video_box = layout.box()
        video_box.label(text="Video Output", icon="FILE_MOVIE")
        
        # Show URL preview
        url_preview = output_prop.value[:50] + "..." if len(output_prop.value) > 50 else output_prop.value
        video_box.label(text=f"URL: {url_preview}")
        
        # Video controls
        controls_row = video_box.row()
        controls_row.operator("runchat.open_video", text="Open Video", icon="PLAY").output_index = index
        controls_row.operator("runchat.save_video", text="Save Video", icon="FILE_FOLDER").output_index = index
        
        # Copy URL button
        copy_row = video_box.row()
        copy_row.operator("runchat.copy_text", text="Copy URL", icon="COPYDOWN").output_index = index
    
    def draw_model_output(self, layout, output_prop, index):
        """Draw 3D model output with controls"""
        model_box = layout.box()
        model_box.label(text="3D Model Output", icon="MESH_DATA")
        
        # Show URL preview and file type
        url_preview = output_prop.value[:50] + "..." if len(output_prop.value) > 50 else output_prop.value
        model_box.label(text=f"URL: {url_preview}")
        
        # Detect model format from URL
        model_format = "Unknown"
        if '.gltf' in output_prop.value.lower():
            model_format = "glTF"
        elif '.glb' in output_prop.value.lower():
            model_format = "GLB"
        elif '.obj' in output_prop.value.lower():
            model_format = "OBJ"
        elif '.fbx' in output_prop.value.lower():
            model_format = "FBX"
        elif '.dae' in output_prop.value.lower():
            model_format = "DAE"
        elif '.blend' in output_prop.value.lower():
            model_format = "Blend"
        
        model_box.label(text=f"Format: {model_format}", icon="INFO")
        
        # Model controls
        controls_row = model_box.row()
        controls_row.operator("runchat.import_model", text="Import to Scene", icon="IMPORT").output_index = index
        controls_row.operator("runchat.save_model", text="Save File", icon="FILE_FOLDER").output_index = index
        
        # Copy URL button
        copy_row = model_box.row()
        copy_row.operator("runchat.copy_text", text="Copy URL", icon="COPYDOWN").output_index = index


class RUNCHAT_PT_execution_panel(Panel):
    bl_label = "Execution"
    bl_idname = "RUNCHAT_PT_execution_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "RUNCHAT_PT_main_panel"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        return runchat_props.schema_loaded
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Main execute button
        exec_row = layout.row()
        exec_row.scale_y = 1.5
        exec_row.operator("runchat.execute", text="Execute Runchat", icon="PLAY")


class RUNCHAT_PT_settings_panel(Panel):
    bl_label = "Settings"
    bl_idname = "RUNCHAT_PT_settings_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "RUNCHAT_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        return runchat_props.schema_loaded
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Image settings
        layout.prop(runchat_props, "auto_save_images")
        layout.prop(runchat_props, "image_save_path")
        
        # Viewport capture settings
        viewport_box = layout.box()
        viewport_box.label(text="Viewport Capture Settings:", icon="CAMERA_DATA")
        capture_row = viewport_box.row()
        capture_row.prop(runchat_props, "viewport_width")
        capture_row.prop(runchat_props, "viewport_height")
        viewport_box.prop(runchat_props, "viewport_quality")
        



class RUNCHAT_PT_help_panel(Panel):
    bl_label = "Help & Debug"
    bl_idname = "RUNCHAT_PT_help_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "RUNCHAT_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Help section
        help_box = layout.box()
        help_box.label(text="Help:", icon="QUESTION")
        help_row = help_box.row()
        help_row.operator("runchat.help", text="Documentation", icon="URL")
        
        # Debug and Testing section
        debug_box = layout.box()
        debug_box.label(text="Debug & Testing:", icon="EXPERIMENTAL")
        
        # API testing row
        api_row = debug_box.row()
        api_row.operator("runchat.test_api_connection", text="Test API", icon="LINKED")
        api_row.operator("runchat.open_info_log", text="Show Info Log", icon="INFO")



classes = [
    RUNCHAT_PT_main_panel,
    RUNCHAT_PT_inputs_panel,
    RUNCHAT_PT_outputs_panel,
    RUNCHAT_PT_execution_panel,
    RUNCHAT_PT_settings_panel,
    RUNCHAT_PT_help_panel,
] 