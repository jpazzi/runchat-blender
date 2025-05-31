import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty
import webbrowser
import importlib
import sys

class RunChatPreferences(AddonPreferences):
    bl_idname = __package__

    api_key: StringProperty(
        name="RunChat API Key",
        description="Your RunChat API key. Get one at runchat.app/dashboard/keys",
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
        box.label(text="RunChat API Configuration:", icon='WORLD_DATA')
        
        row = box.row()
        row.prop(self, "api_key", text="API Key")
        
        row = box.row()
        row.operator("runchat.open_api_keys", text="Get API Key", icon='URL')
        row.operator("runchat.open_docs", text="Documentation", icon='HELP')
        
        # PIL Status section
        box = layout.box()
        box.label(text="Image Processing:", icon='IMAGE_DATA')
        
        try:
            from . import utils
            if utils.PIL_AVAILABLE:
                row = box.row()
                row.label(text="✅ PIL/Pillow: Available", icon='CHECKMARK')
                row = box.row()
                row.label(text="Enhanced image compression enabled")
            else:
                row = box.row()
                row.alert = True
                row.label(text="⚠️ PIL/Pillow: Not Available", icon='ERROR')
                row = box.row()
                row.label(text="Basic image processing only (no compression)")
                row = box.row()
                row.operator("runchat.install_pil", text="Install PIL/Pillow", icon='IMPORT')
        except:
            pass
        
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
    """Open RunChat API keys page"""
    bl_idname = "runchat.open_api_keys"
    bl_label = "Open API Keys Page"
    
    def execute(self, context):
        webbrowser.open("https://runchat.app/dashboard/keys")
        return {'FINISHED'}

class RUNCHAT_OT_OpenDocs(bpy.types.Operator):
    """Open RunChat documentation"""
    bl_idname = "runchat.open_docs"
    bl_label = "Open Documentation"
    
    def execute(self, context):
        webbrowser.open("https://docs.runchat.app")
        return {'FINISHED'}

class RUNCHAT_OT_ReloadAddon(bpy.types.Operator):
    """Hot reload the RunChat addon modules"""
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
            print(f"RunChat addon hot reload complete: {reloaded_count} modules")
            
        except Exception as e:
            self.report({'ERROR'}, f"Hot reload failed: {str(e)}")
            print(f"Hot reload error: {e}")
        
        return {'FINISHED'}

class RUNCHAT_OT_RestartAddon(bpy.types.Operator):
    """Restart the RunChat addon completely"""
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

class RUNCHAT_OT_InstallPIL(bpy.types.Operator):
    """Install PIL/Pillow for Blender"""
    bl_idname = "runchat.install_pil"
    bl_label = "Install PIL/Pillow"
    
    def execute(self, context):
        try:
            import subprocess
            import sys
            
            # Get Blender's Python executable
            python_exe = sys.executable
            
            self.report({'INFO'}, "Installing PIL/Pillow... This may take a moment.")
            
            # Install Pillow using Blender's Python
            result = subprocess.run([
                python_exe, "-m", "pip", "install", "Pillow"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.report({'INFO'}, "PIL/Pillow installed successfully! Please restart Blender.")
            else:
                self.report({'ERROR'}, f"Installation failed: {result.stderr}")
                # Show manual installation instructions
                self.report({'INFO'}, "Try manual installation: see System Console for details")
                print("=" * 50)
                print("MANUAL PIL INSTALLATION INSTRUCTIONS:")
                print("=" * 50)
                print(f"1. Open Terminal/Command Prompt")
                print(f"2. Run: {python_exe} -m pip install Pillow")
                print(f"3. Restart Blender")
                print("=" * 50)
            
        except Exception as e:
            self.report({'ERROR'}, f"Installation error: {str(e)}")
            print("=" * 50)
            print("ALTERNATIVE INSTALLATION METHODS:")
            print("=" * 50)
            print("Method 1 - Blender Python:")
            print("  import subprocess, sys")
            print("  subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'])")
            print("")
            print("Method 2 - External Python:")
            print("  pip install Pillow")
            print("  (Make sure you're using the same Python version as Blender)")
            print("=" * 50)
        
        return {'FINISHED'}

def get_api_key():
    """Helper function to get the API key from preferences"""
    preferences = bpy.context.preferences.addons[__package__].preferences
    return preferences.api_key

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
    RUNCHAT_OT_InstallPIL,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls) 