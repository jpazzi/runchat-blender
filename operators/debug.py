# operators/debug.py

import bpy
import os
import requests
from bpy.types import Operator

from .. import api
from .. import preferences


def log_to_blender(message, level='INFO'):
    """Log message to Blender's Info log"""
    print(f"[Runchat Debug] {message}")
    # Add to Blender's info reports (visible in Info editor)
    try:
        if level == 'ERROR':
            bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=f"Runchat: {message}"), title="Runchat Error", icon='ERROR')
        # For now, we'll rely on print() and the operator's self.report()
    except:
        pass




class RUNCHAT_OT_test_api_connection(Operator):
    """Test API connection and basic functionality"""
    bl_idname = "runchat.test_api_connection"
    bl_label = "Test API Connection"
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Test basic connectivity
        log_to_blender("=== TESTING API CONNECTION ===")
        
        api_key = preferences.get_api_key()
        if not api_key:
            self.report({'ERROR'}, "Please set your Runchat API key first")
            log_to_blender("No API key set", 'ERROR')
            return {'CANCELLED'}
        
        log_to_blender(f"API Key present: Yes ({len(api_key)} characters)")
        
        # Test basic HTTP connectivity
        try:
            log_to_blender("Testing basic HTTP connectivity...")
            response = requests.get("https://httpbin.org/get", timeout=10)
            log_to_blender(f"HTTP test successful: {response.status_code}")
        except Exception as e:
            log_to_blender(f"HTTP test failed: {e}", 'ERROR')
            self.report({'ERROR'}, f"HTTP connectivity test failed: {e}")
            return {'CANCELLED'}
        
        # Test Runchat API connectivity
        if runchat_props.runchat_id:
            log_to_blender(f"Testing Runchat API with ID: {runchat_props.runchat_id}")
            try:
                schema = api.RunChatAPI.get_schema(runchat_props.runchat_id, api_key)
                if schema:
                    log_to_blender("Schema API test successful!")
                    log_to_blender(f"Schema keys: {list(schema.keys()) if isinstance(schema, dict) else 'Not a dict'}")
                    self.report({'INFO'}, "API connection test successful!")
                else:
                    log_to_blender("Schema API test failed - no result", 'ERROR')
                    self.report({'WARNING'}, "API connection test failed - check logs")
            except Exception as e:
                log_to_blender(f"Schema API test failed: {e}", 'ERROR')
                self.report({'ERROR'}, f"API test failed: {e}")
                return {'CANCELLED'}
        else:
            log_to_blender("No Runchat ID set - skipping schema test", 'WARNING')
            self.report({'INFO'}, "Basic connectivity OK - set Runchat ID to test schema API")
        
        log_to_blender("=== API CONNECTION TEST COMPLETE ===")
        return {'FINISHED'}





class RUNCHAT_OT_open_info_log(Operator):
    """Show instructions for viewing the Info log"""
    bl_idname = "runchat.open_info_log"
    bl_label = "Show Info Log Instructions"
    
    def execute(self, context):
        log_to_blender("=== HOW TO VIEW BLENDER INFO LOG ===")
        log_to_blender("1. Go to Window > Toggle System Console (Windows/Linux)")
        log_to_blender("   OR Window > New Window > Console (macOS)")
        log_to_blender("2. OR change an area to Info Editor:")
        log_to_blender("   - Click on Editor Type icon in any area")
        log_to_blender("   - Select 'Info' from the dropdown")
        log_to_blender("3. All Runchat debug messages appear here")
        log_to_blender("4. Look for messages starting with '[Runchat]'")
        log_to_blender("=== END INSTRUCTIONS ===")
        
        self.report({'INFO'}, "Info log instructions printed - check console or Info editor")
        return {'FINISHED'}


classes = [
    RUNCHAT_OT_test_api_connection,
    RUNCHAT_OT_open_info_log,
] 