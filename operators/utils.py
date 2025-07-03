# operators/utils.py

import bpy
import webbrowser
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty



class RUNCHAT_OT_copy_text(Operator):
    """Copy text output to clipboard"""
    bl_idname = "runchat.copy_text"
    bl_label = "Copy Text"
    
    output_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if self.output_index >= len(runchat_props.outputs):
            self.report({'ERROR'}, "Invalid output index")
            return {'CANCELLED'}
        
        output_prop = runchat_props.outputs[self.output_index]
        
        if not output_prop.value:
            self.report({'ERROR'}, "No text to copy")
            return {'CANCELLED'}
        
        try:
            context.window_manager.clipboard = output_prop.value
            self.report({'INFO'}, "Text copied to clipboard")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to copy text: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class RUNCHAT_OT_open_editor(Operator):
    """Open RunChat editor"""
    bl_idname = "runchat.open_editor"
    bl_label = "Open Editor"
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if not runchat_props.runchat_id:
            self.report({'ERROR'}, "Please enter a RunChat ID")
            return {'CANCELLED'}
        
        url = f"https://runchat.app/editor?id={runchat_props.runchat_id}"
        webbrowser.open(url)
        return {'FINISHED'}


class RUNCHAT_OT_help(Operator):
    """Open RunChat documentation"""
    bl_idname = "runchat.help"
    bl_label = "Open Documentation"
    
    def execute(self, context):
        webbrowser.open("https://docs.runchat.app")
        return {'FINISHED'}


class RUNCHAT_OT_youtube_tutorials(Operator):
    """Open RunChat YouTube tutorials"""
    bl_idname = "runchat.youtube_tutorials"
    bl_label = "Open YouTube Tutorials"
    
    def execute(self, context):
        webbrowser.open("https://www.youtube.com/playlist?list=PLgT771y9VleA_56wwK7nqcuplAJWzpi8_")
        return {'FINISHED'}


class RUNCHAT_OT_open_link(Operator):
    """Open a URL from markdown link in description"""
    bl_idname = "runchat.open_link"
    bl_label = "Open Link"
    
    url: StringProperty(name="URL")
    
    def execute(self, context):
        if not self.url:
            self.report({'ERROR'}, "No URL provided")
            return {'CANCELLED'}
        
        try:
            webbrowser.open(self.url)
            self.report({'INFO'}, f"Opened: {self.url}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open URL: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


# Classes to register
classes = [
    RUNCHAT_OT_copy_text,
    RUNCHAT_OT_open_editor,
    RUNCHAT_OT_help,
    RUNCHAT_OT_youtube_tutorials,
    RUNCHAT_OT_open_link,
] 