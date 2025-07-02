import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty
import webbrowser

class RunChatPreferences(AddonPreferences):
    bl_idname = __package__

    api_key: StringProperty(
        name="Runchat API Key",
        description="Your Runchat API key. Get one at https://runchat.app/signup/blender",
        default="",
        subtype='PASSWORD'
    )

    def draw(self, context):
        layout = self.layout
        
        # API Key section
        box = layout.box()
        box.label(text="Runchat API Configuration:", icon='WORLD_DATA')
        
        row = box.row()
        row.prop(self, "api_key", text="API Key")
        
        row = box.row()
        row.operator("runchat.open_api_keys", text="Get API Key", icon='URL')
        row.operator("runchat.open_docs", text="Documentation", icon='HELP')

class RUNCHAT_OT_OpenApiKeys(bpy.types.Operator):
    """Open Runchat API keys page"""
    bl_idname = "runchat.open_api_keys"
    bl_label = "Open API Keys Page"
    
    def execute(self, context):
        webbrowser.open("https://runchat.app/signup/blender")
        return {'FINISHED'}

class RUNCHAT_OT_OpenDocs(bpy.types.Operator):
    """Open Runchat documentation"""
    bl_idname = "runchat.open_docs"
    bl_label = "Open Documentation"
    
    def execute(self, context):
        webbrowser.open("https://docs.runchat.app")
        return {'FINISHED'}

def get_api_key():
    """Helper function to get the API key from preferences"""
    try:
        preferences = bpy.context.preferences.addons[__package__].preferences
        return preferences.api_key
    except (KeyError, AttributeError):
        print("Warning: Runchat addon preferences not found")
        return ""

classes = [
    RunChatPreferences,
    RUNCHAT_OT_OpenApiKeys,
    RUNCHAT_OT_OpenDocs,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls) 