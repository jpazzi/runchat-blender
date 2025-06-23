import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty
import webbrowser
import importlib
import sys

class RunChatPreferences(AddonPreferences):
    bl_idname = __package__

    api_key: StringProperty(
        name="Runchat API Key",
        description="Your Runchat API key. Get one at runchat.app/dashboard/keys",
        default="",
        subtype='PASSWORD'
    )
    
    development_mode: BoolProperty(
        name="Development Mode",
        description="Enable development features and hot reload",
        default=False
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
        
        # Development section
        box = layout.box()
        box.label(text="Development:", icon='TOOL_SETTINGS')
        
        row = box.row()
        row.prop(self, "development_mode", text="Enable Development Mode")
        
        if self.development_mode:
            row = box.row()
            row.operator("runchat.reload_addon", text="Hot Reload Addon", icon='FILE_REFRESH')
            row.operator("runchat.restart_addon", text="Restart Addon", icon='RECOVER_LAST')

class RUNCHAT_OT_OpenApiKeys(bpy.types.Operator):
    """Open Runchat API keys page"""
    bl_idname = "runchat.open_api_keys"
    bl_label = "Open API Keys Page"
    
    def execute(self, context):
        webbrowser.open("https://runchat.app/dashboard/keys")
        return {'FINISHED'}

class RUNCHAT_OT_OpenDocs(bpy.types.Operator):
    """Open Runchat documentation"""
    bl_idname = "runchat.open_docs"
    bl_label = "Open Documentation"
    
    def execute(self, context):
        webbrowser.open("https://docs.runchat.app")
        return {'FINISHED'}

class RUNCHAT_OT_ReloadAddon(bpy.types.Operator):
    """Hot reload the Runchat addon modules"""
    bl_idname = "runchat.reload_addon"
    bl_label = "Hot Reload Addon"
    
    def execute(self, context):
        try:
            # Get the addon package name
            addon_name = __package__.split('.')[0] if '.' in __package__ else __package__
            
            # Find all modules belonging to this addon
            addon_modules = []
            for module_name in list(sys.modules.keys()):
                if module_name.startswith(addon_name):
                    addon_modules.append(module_name)
            
            # Reload modules in reverse order (dependencies first)
            reloaded_count = 0
            for module_name in reversed(addon_modules):
                if module_name in sys.modules:
                    try:
                        importlib.reload(sys.modules[module_name])
                        reloaded_count += 1
                        print(f"Reloaded: {module_name}")
                    except Exception as e:
                        print(f"Failed to reload {module_name}: {e}")
            
            self.report({'INFO'}, f"Hot reloaded {reloaded_count} modules")
            print(f"Runchat addon hot reload complete: {reloaded_count} modules")
            
        except Exception as e:
            self.report({'ERROR'}, f"Hot reload failed: {str(e)}")
            print(f"Hot reload error: {e}")
        
        return {'FINISHED'}

class RUNCHAT_OT_RestartAddon(bpy.types.Operator):
    """Restart the Runchat addon completely"""
    bl_idname = "runchat.restart_addon"
    bl_label = "Restart Addon"
    
    def execute(self, context):
        try:
            addon_name = __package__.split('.')[0] if '.' in __package__ else __package__
            
            # Disable addon
            bpy.ops.preferences.addon_disable(module=addon_name)
            
            # Enable addon
            bpy.ops.preferences.addon_enable(module=addon_name)
            
            self.report({'INFO'}, "Addon restarted successfully")
            
        except Exception as e:
            self.report({'ERROR'}, f"Restart failed: {str(e)}")
        
        return {'FINISHED'}

def get_api_key():
    """Helper function to get the API key from preferences"""
    try:
        preferences = bpy.context.preferences.addons[__package__].preferences
        return preferences.api_key
    except (KeyError, AttributeError):
        print("Warning: Runchat addon preferences not found")
        return ""

def is_development_mode():
    """Helper function to check if development mode is enabled"""
    try:
        preferences = bpy.context.preferences.addons[__package__].preferences
        return preferences.development_mode
    except:
        return False

classes = [
    RunChatPreferences,
    RUNCHAT_OT_OpenApiKeys,
    RUNCHAT_OT_OpenDocs,
    RUNCHAT_OT_ReloadAddon,
    RUNCHAT_OT_RestartAddon,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls) 