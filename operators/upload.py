# operators/upload.py

import bpy
import base64
import os
from bpy.types import Operator
from bpy.props import IntProperty

from .. import api
from .. import preferences


class RUNCHAT_OT_upload_file(Operator):
    """Upload selected file to RunChat"""
    bl_idname = "runchat.upload_file"
    bl_label = "Upload File"
    
    input_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.input_index >= len(runchat_props.inputs):
            self.report({'ERROR'}, "Invalid input index")
            return {'CANCELLED'}
        
        input_prop = runchat_props.inputs[self.input_index]
        
        if not input_prop.file_path:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}
        
        # Get API key
        api_key = preferences.get_api_key()
        if not api_key:
            self.report({'ERROR'}, "Please set your RunChat API key in addon preferences")
            return {'CANCELLED'}
        
        try:
            # Update status
            input_prop.upload_status = "Reading file..."
            
            # Read and encode file
            file_path = bpy.path.abspath(input_prop.file_path)
            if not os.path.exists(file_path):
                input_prop.upload_status = "File not found"
                self.report({'ERROR'}, "File not found")
                return {'CANCELLED'}
            
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
                base64_data = base64.b64encode(image_bytes).decode('utf-8')
            
            # Upload to RunChat
            input_prop.upload_status = "Uploading to RunChat..."
            filename = os.path.basename(file_path)
            
            uploaded_url = api.RunChatAPI.upload_image(base64_data, filename, api_key)
            
            if uploaded_url:
                input_prop.uploaded_url = uploaded_url
                input_prop.text_value = uploaded_url  # Also set as text value for execution
                input_prop.upload_status = "Upload successful!"
                self.report({'INFO'}, f"File uploaded successfully: {uploaded_url}")
            else:
                input_prop.upload_status = "Upload failed"
                self.report({'ERROR'}, "Failed to upload file to RunChat")
                return {'CANCELLED'}
                
        except Exception as e:
            input_prop.upload_status = f"Error: {str(e)}"
            self.report({'ERROR'}, f"Error uploading file: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


# Classes to register
classes = [
    RUNCHAT_OT_upload_file,
] 