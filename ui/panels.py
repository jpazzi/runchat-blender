# ui/panels.py

import bpy
from bpy.types import Panel

from . import helpers
from .. import preferences


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
        
        # Get API key to determine what to show
        api_key = preferences.get_api_key()
        
        # API Key section (only shown when no API key is set)
        if not api_key:
            api_box = layout.box()
            api_box.label(text="API Configuration:", icon="WORLD_DATA")
            
            # Warning section with alert styling
            warning_box = api_box.box()
            warning_box.alert = True  # Make warning highlighted in red
            api_warning = warning_box.row()
            api_warning.scale_y = 1.2
            api_warning.label(text="API Key Required", icon="ERROR")
            
            api_help = warning_box.row()
            api_help.scale_y = 0.9
            api_help.label(text="Enter your Runchat API key below to get started")
            
            api_help2 = warning_box.row()
            api_help2.scale_y = 0.9
            api_help2.label(text="If you don't have a Runchat API key, you can get one by signing up to Runchat using the button below")
            
            # API key input field
            try:
                addon_prefs = context.preferences.addons["runchat-blender"].preferences
                api_input_row = api_box.row()
                api_input_row.prop(addon_prefs, "api_key", text="API Key")
            except (KeyError, AttributeError):
                api_box.label(text="Error: Cannot access preferences", icon="ERROR")
            
            # API key configuration buttons
            api_buttons = api_box.row()
            api_buttons.operator("runchat.open_api_keys", text="Get API Key", icon="URL")
            
            # Add preferences button as backup
            api_buttons.operator("screen.userpref_show", text="Preferences", icon="PREFERENCES")
        
        # Version Update section (always shown)
        # Use getattr with defaults for backwards compatibility
        version_checked = getattr(runchat_props, 'version_checked', False)
        update_available = getattr(runchat_props, 'update_available', False)
        
        if version_checked and update_available:
            # Create a prominent update notification box
            update_box = layout.box()
            update_box.alert = True  # Makes the box highlighted in red
            
            # Main header with eye-catching icon
            update_header = update_box.row()
            update_header.scale_y = 1.2  # Make it taller
            update_header.label(text="Runchat Plugin Update Available!", icon="ERROR")
            
            # Version information
            version_row = update_box.row()
            latest_version = getattr(runchat_props, 'latest_version', 'Unknown')
            version_row.label(text=f"Latest Version: v{latest_version} - New features & fixes available")
            
            # Prominent download button
            download_row = update_box.row()
            download_row.scale_y = 1.6  # Make button bigger
            download_op = download_row.operator("runchat.download_update", text="Download Latest Package", icon="IMPORT")
            download_row.alert = True  # Make button highlighted in red
            
            # Release notes dropdown section
            if hasattr(runchat_props, 'release_notes') and len(runchat_props.release_notes) > 0:
                # Collapsible release notes header
                notes_header = update_box.row()
                notes_header.prop(runchat_props, "show_release_notes", 
                                icon="TRIA_DOWN" if runchat_props.show_release_notes else "TRIA_RIGHT",
                                icon_only=True, emboss=False)
                notes_header.label(text="What's new in this update")
                
                # Show release notes content when expanded
                if runchat_props.show_release_notes:
                    notes_box = update_box.box()
                    notes_box.scale_y = 0.9
                    
                    # Show release notes for the latest version
                    latest_release = runchat_props.release_notes[0]  # Assuming sorted by version (latest first)
                    version_row = notes_box.row()
                    version_row.scale_y = 0.8
                    version_row.label(text=f"Version {latest_release.version} ({latest_release.date})")
                    
                    # Parse and display release items
                    try:
                        import json
                        items = json.loads(latest_release.items)
                        for item in items:  # Show all items when expanded
                            item_row = notes_box.row()
                            item_row.scale_y = 0.7
                            item_row.label(text=item)
                            
                    except (json.JSONDecodeError, AttributeError):
                        # Fallback if JSON parsing fails
                        fallback_row = notes_box.row()
                        fallback_row.scale_y = 0.8
                        fallback_row.label(text="New features and improvements available")
            else:
                # Fallback to generic message if no release notes available
                help_row = update_box.row()
                help_row.scale_y = 0.8
                help_row.label(text="Click to download and manually install the new version")
            
            # Separator after update notification
            layout.separator()

        # Credit Error section (shown prominently when there's a credit error)
        if api_key and hasattr(runchat_props, 'has_credit_error') and runchat_props.has_credit_error:
            # Create a prominent credit error notification box
            credit_error_box = layout.box()
            credit_error_box.alert = True  # Makes the box highlighted in red
            
            # Main header with eye-catching icon
            error_header = credit_error_box.row()
            error_header.scale_y = 1.2  # Make it taller
            error_header.label(text="Credits Exhausted - Workflow Failed!", icon="ERROR")
            
            # Error message
            if hasattr(runchat_props, 'credit_error_message') and runchat_props.credit_error_message:
                message_row = credit_error_box.row()
                message_row.label(text=runchat_props.credit_error_message)
            else:
                message_row = credit_error_box.row()
                message_row.label(text="You have reached your credit limit for this billing period.")
            
            # Action buttons
            actions_row = credit_error_box.row()
            actions_row.scale_y = 1.4  # Make buttons bigger
            
            # Pricing button
            actions_row.operator("runchat.pricing", text="Get More Credits", icon="FUND")
            
            # Separator after credit error notification
            layout.separator()

        # Only show workflow sections if API key is configured
        if not api_key:
            # Show message encouraging API key setup
            help_box = layout.box()
            help_box.scale_y = 0.9
            help_row = help_box.row()
            help_row.alignment = 'CENTER'
            help_row.label(text="Configure your API key above to start using Runchat workflows", icon="INFO")
            return
        
        # Workflow Examples section (only when API key is set)
        examples_box = layout.box()
        examples_header = examples_box.row()
        examples_header.prop(runchat_props, "show_examples", 
                           icon="TRIA_DOWN" if runchat_props.show_examples else "TRIA_RIGHT",
                           icon_only=True, emboss=False)
        examples_header.label(text="Select a Workflow")
        
        if runchat_props.show_examples:
            if runchat_props.examples_loading:
                # Show loading state
                loading_row = examples_box.row()
                loading_row.label(text="Loading examples...", icon="TIME")
            elif len(runchat_props.examples) == 0:
                if runchat_props.examples_loaded:
                    examples_box.label(text="No examples available", icon="INFO")
                else:
                    # Show manual load button - no auto-loading
                    examples_box.operator("runchat.load_examples", text="Load Examples")
                    hint_row = examples_box.row()
                    hint_row.scale_y = 0.8
                    hint_row.label(text="Click to load workflow examples", icon="INFO")
            else:
                # Show loaded examples (sorted alphabetically)
                sorted_examples = sorted(runchat_props.examples, key=lambda x: x.name.lower())
                for i, example in enumerate(sorted_examples):
                    example_row = examples_box.row()
                    op = example_row.operator("runchat.use_example", text=example.name)
                    op.example_id = example.example_id
        
        # Main controls (runchat ID input)
        examples_box.label(text="Load by ID:")
        row = examples_box.row()
        row.prop(runchat_props, "runchat_id", text="")
        row.operator("runchat.load_schema", text="", icon="LINKED")

        layout.separator()
            
        # Workflow info
        if runchat_props.schema_loaded:
            box = layout.box()
            box.label(text=f"{runchat_props.workflow_name}", icon="FILE_SCRIPT")
            
            # Open in Editor and Clear Workflow buttons (only show when schema is loaded)
            if runchat_props.runchat_id:
                editor_row = box.row()
                editor_row.operator("runchat.open_editor", text="Open in Editor", icon="URL")
                editor_row.operator("runchat.clear_workflow", text="Clear Workflow", icon="TRASH")



class RUNCHAT_PT_inputs_panel(Panel):
    bl_label = "Inputs"
    bl_idname = "RUNCHAT_PT_inputs_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "RUNCHAT_PT_main_panel"
    
    @classmethod
    def poll(cls, context):
        # Only show if API key is configured and schema is loaded with inputs
        api_key = preferences.get_api_key()
        if not api_key:
            return False
            
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
            
            # File upload option
            file_section = upload_content.box()
            file_section.label(text="File Upload:", icon="FILE_FOLDER")
            file_row = file_section.row()
            file_row.prop(input_prop, "file_path", text="")
            
            if input_prop.file_path:
                upload_row = file_section.row()
                upload_row.operator("runchat.upload_file", text="Upload Selected File", icon="EXPORT").input_index = index
            
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
        # Only show if API key is configured and schema is loaded with outputs
        api_key = preferences.get_api_key()
        if not api_key:
            return False
            
        scene = context.scene
        runchat_props = scene.runchat_properties
        return runchat_props.schema_loaded and len(runchat_props.outputs) > 0
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Status section
        if runchat_props.status != "Ready":
            status_box = layout.box()
            status_box.label(text=f"Status: {runchat_props.status}", icon="INFO")
        
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
        
        # Header with video icon and info
        header_row = video_box.row()
        header_row.label(text="Video Output", icon="FILE_MOVIE")
        
        # Show URL preview
        url_preview = output_prop.value[:50] + "..." if len(output_prop.value) > 50 else output_prop.value
        video_box.label(text=f"URL: {url_preview}")
        
        # Check if video sequences exist in the current scene (indicating auto-import happened)
        scene = bpy.context.scene
        has_video_sequences = (scene.sequence_editor and 
                              len(scene.sequence_editor.sequences) > 0 and
                              any(seq.type == 'MOVIE' for seq in scene.sequence_editor.sequences))
        
        if has_video_sequences:
            # Show auto-import status
            import_status_box = video_box.box()
            import_status_box.alert = False  # Use normal coloring
            status_row = import_status_box.row()
            status_row.label(text="Auto-imported to Video Sequencer", icon="CHECKMARK")
            
            # Quick action to open sequencer
            action_row = import_status_box.row()
            action_row.operator("runchat.open_video_editor", text="Open Video Sequencer", icon="SEQUENCE")
        else:
            # Primary action - Import to Video Sequencer (most prominent)
            import_box = video_box.box()
            import_box.alert = True  # Make it stand out
            import_row = import_box.row()
            import_row.scale_y = 1.5  # Make button bigger
            import_op = import_row.operator("runchat.import_video", text="⚡ Import to Video Sequencer", icon="SEQUENCE")
            import_op.output_index = index
        
        # Secondary actions (always available)
        controls_row = video_box.row()
        controls_row.operator("runchat.open_video", text="Open in Browser", icon="PLAY").output_index = index
        controls_row.operator("runchat.save_video", text="Save to File", icon="FILE_FOLDER").output_index = index
        
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
        # Only show if API key is configured
        api_key = preferences.get_api_key()
        if not api_key:
            return False
            
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Show panel if schema is loaded OR if execution is in progress
        is_executing = ("Executing" in runchat_props.status or 
                       "processing" in runchat_props.status.lower() or
                       "Starting" in runchat_props.status or
                       (runchat_props.progress > 0.0 and runchat_props.progress < 1.0))
        
        return runchat_props.schema_loaded or is_executing
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Check if execution is in progress
        is_executing = ("Executing" in runchat_props.status or 
                       "processing" in runchat_props.status.lower() or
                       "Starting" in runchat_props.status or
                       (runchat_props.progress > 0.0 and runchat_props.progress < 1.0))
        
        # Main execute/cancel button
        exec_row = layout.row()
        exec_row.scale_y = 1.5
        
        if is_executing:
            # Show status when executing (no cancel button since operator doesn't exist)
            exec_row.alert = True
            exec_row.label(text="Executing Workflow...", icon="TIME")
        else:
            # Show execute button when not executing
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
        # Only show if API key is configured and schema is loaded
        api_key = preferences.get_api_key()
        if not api_key:
            return False
            
        scene = context.scene
        runchat_props = scene.runchat_properties
        return runchat_props.schema_loaded
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Save paths settings
        save_box = layout.box()
        save_box.label(text="Save Paths:", icon="FILE_FOLDER")
        save_box.prop(runchat_props, "auto_save_images")
        save_box.prop(runchat_props, "image_save_path")
        save_box.prop(runchat_props, "video_save_path")
        
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
    
    @classmethod
    def poll(cls, context):
        # Only show if API key is configured
        api_key = preferences.get_api_key()
        return bool(api_key)
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Version information (display only, no manual actions needed)
        version_box = layout.box()
        version_box.label(text="Plugin Version:", icon="INFO")
        
        # Get current version from bl_info
        try:
            from .. import bl_info
            current_version = ".".join(map(str, bl_info["version"]))
            version_box.label(text=f"Installed: v{current_version}")
        except:
            version_box.label(text="Installed: Unknown")
        
        # Show update status if checked (but no manual action buttons)
        if runchat_props.version_checked:
            if runchat_props.latest_version:
                version_box.label(text=f"Latest Available: v{runchat_props.latest_version}")
            
            if not runchat_props.update_available:
                status_row = version_box.row()
                status_row.label(text="Up to date", icon="CHECKMARK")
        
        layout.separator()
        
        # Help section
        help_box = layout.box()
        help_box.label(text="Help:", icon="QUESTION")
        help_row = help_box.row()
        help_row.operator("runchat.help", text="Documentation", icon="URL")
        help_row.operator("runchat.youtube_tutorials", text="YouTube Tutorials", icon="PLAY")
        
        # Debug and Testing section
        debug_box = layout.box()
        debug_box.label(text="Debug & Testing:", icon="EXPERIMENTAL")
        
        # API testing row
        api_row = debug_box.row()
        api_row.operator("runchat.test_api_connection", text="Test API", icon="LINKED")
        api_row.operator("runchat.test_dependencies", text="Test Dependencies", icon="SYSTEM")
        
        # Info log row
        info_row = debug_box.row()
        info_row.operator("runchat.open_info_log", text="Show Info Log", icon="INFO")



classes = [
    RUNCHAT_PT_main_panel,
    RUNCHAT_PT_inputs_panel,
    RUNCHAT_PT_outputs_panel,
    RUNCHAT_PT_execution_panel,
    RUNCHAT_PT_settings_panel,
    RUNCHAT_PT_help_panel,
] 