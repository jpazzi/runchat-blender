# properties.py

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty, 
    BoolProperty, 
    EnumProperty, 
    IntProperty, 
    FloatProperty,
    CollectionProperty,
)

class RunChatExampleProperty(PropertyGroup):
    """Property group for storing workflow examples"""
    example_id: StringProperty(name="Example ID")
    name: StringProperty(name="Example Name")

class RunChatInputProperty(PropertyGroup):
    param_id: StringProperty(name="Parameter ID")
    node_id: StringProperty(name="Node ID")
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    data_type: StringProperty(name="Data Type")
    ui_type: StringProperty(name="UI Type", default="text")
    required: BoolProperty(name="Required")
    
    text_value: StringProperty(
        name="Text Value", 
        description="Enter your text input (supports multiline)",
        options={'TEXTEDIT_UPDATE'},
        maxlen=0  # Remove character limit for long text
    )
    file_path: StringProperty(name="File Path", subtype='FILE_PATH')
    use_viewport_capture: BoolProperty(name="Use Viewport Capture")
    
    uploaded_url: StringProperty(name="Uploaded URL")
    upload_status: StringProperty(name="Upload Status", default="")



class RunChatOutputProperty(PropertyGroup):
    param_id: StringProperty(name="Parameter ID")
    node_id: StringProperty(name="Node ID")
    name: StringProperty(name="Name")
    data_type: StringProperty(name="Data Type")
    value: StringProperty(name="Value")
    
    output_type: StringProperty(name="Output Type")
    is_processed: BoolProperty(name="Is Processed", default=False)

class RunChatProperties(PropertyGroup):
    runchat_id: StringProperty(name="Runchat ID", description="The unique identifier for the Runchat workflow", default="")
    schema_loaded: BoolProperty(name="Schema Loaded", default=False)
    workflow_name: StringProperty(name="Workflow Name", default="")
    status: StringProperty(name="Status", default="Ready")
    instance_id: StringProperty(name="Instance ID", default="")
    
    inputs: CollectionProperty(type=RunChatInputProperty)
    outputs: CollectionProperty(type=RunChatOutputProperty)
    examples: CollectionProperty(type=RunChatExampleProperty)
    
    show_inputs: BoolProperty(name="Show Inputs", default=True)
    show_outputs: BoolProperty(name="Show Outputs", default=True)
    show_advanced: BoolProperty(name="Show Advanced", default=False)
    show_examples: BoolProperty(name="Show Examples", default=True)
    examples_loaded: BoolProperty(name="Examples Loaded", default=False)
    examples_loading: BoolProperty(name="Examples Loading", default=False)
    
    auto_save_images: BoolProperty(name="Auto Save Images", description="Automatically save output images to disk", default=True)
    image_save_path: StringProperty(name="Image Save Path", description="Directory to save output images", default="~/Desktop/Runchat_outputs/", subtype='DIR_PATH')
    video_save_path: StringProperty(name="Video Save Path", description="Directory to save output videos", default="~/Desktop/Runchat_outputs/", subtype='DIR_PATH')
    
    viewport_width: IntProperty(name="Capture Width", default=1920, min=64, max=8192)
    viewport_height: IntProperty(name="Capture Height", default=1080, min=64, max=8192)
    viewport_quality: IntProperty(name="Image Quality", default=90, min=1, max=100)
    
    progress: FloatProperty(name="Progress", min=0.0, max=1.0, default=0.0)
    progress_message: StringProperty(name="Progress Message", default="")


classes = [
    RunChatExampleProperty,
    RunChatInputProperty,
    RunChatOutputProperty,
    RunChatProperties,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)