# operators/debug.py

import bpy
import os
from bpy.types import Operator

from .. import api
from .. import preferences
from ..utils.dependencies import get_requests, check_dependencies

# Get bundled requests
requests, _ = get_requests()


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


class RUNCHAT_OT_clear_workflow(Operator):
    """Clear current Runchat workflow and reset addon state"""
    bl_idname = "runchat.clear_workflow"
    bl_label = "Clear Workflow"
    bl_description = "Clear all workflow data and reset the addon"
    
    def execute(self, context):
        try:
            scene = context.scene
            runchat_props = scene.runchat_properties
            
            log_to_blender("=== CLEARING RUNCHAT WORKFLOW ===")
            
            # Clear workflow data
            runchat_props.runchat_id = ""
            runchat_props.schema_loaded = False
            runchat_props.workflow_name = ""
            runchat_props.status = "Ready"
            runchat_props.instance_id = ""
            
            # Clear progress
            runchat_props.progress = 0.0
            runchat_props.progress_message = ""
            
            # Clear inputs
            runchat_props.inputs.clear()
            log_to_blender(f"Cleared {len(runchat_props.inputs)} input properties")
            
            # Clear outputs
            runchat_props.outputs.clear()
            log_to_blender(f"Cleared {len(runchat_props.outputs)} output properties")
            
            # Clear any loaded images from this workflow
            images_cleared = 0
            for image in list(bpy.data.images):
                # Clear images that start with common Runchat prefixes
                if (image.name.startswith('Media') or 
                    image.name.startswith('RunChat_Image') or 
                    image.name.startswith('Runchat_Image')):
                    bpy.data.images.remove(image)
                    images_cleared += 1
            
            if images_cleared > 0:
                log_to_blender(f"Cleared {images_cleared} workflow images from Blender")
            
            # Force UI refresh
            for area in bpy.context.screen.areas:
                if area.type == 'PROPERTIES':
                    area.tag_redraw()
            
            log_to_blender("Workflow cleared successfully")
            self.report({'INFO'}, "Runchat workflow cleared successfully")
            
        except Exception as e:
            log_to_blender(f"Error clearing workflow: {e}", 'ERROR')
            self.report({'ERROR'}, f"Error clearing workflow: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class RUNCHAT_OT_test_dependencies(Operator):
    """Test and report on bundled dependencies"""
    bl_idname = "runchat.test_dependencies" 
    bl_label = "Test Dependencies"
    bl_description = "Test availability and functionality of bundled dependencies"
    
    def execute(self, context):
        log_to_blender("=== BUNDLED DEPENDENCY TEST ===")
        
        try:
            # Check bundled dependencies
            deps = check_dependencies()
            
            # Report results
            requests_status = deps['requests_backend']
            pil_status = "Available" if deps['pil_available'] else "Not available"
            
            log_to_blender(f"Bundled Requests: {requests_status}")
            log_to_blender(f"Bundled PIL/Pillow: {pil_status}")
            
            log_to_blender("✅ Using bundled requests library")
            log_to_blender("✅ Using bundled PIL/Pillow library")
            
            # Test basic HTTP functionality
            try:
                log_to_blender("Testing bundled requests functionality...")
                response = deps['requests'].get("https://httpbin.org/get", timeout=10)
                log_to_blender(f"✅ HTTP test successful: {response.status_code}")
            except Exception as e:
                log_to_blender(f"❌ HTTP test failed: {e}")
                raise
            
            # Test PIL functionality
            try:
                log_to_blender("Testing bundled PIL functionality...")
                # Create a small test image
                test_img = deps['pil'].new('RGB', (10, 10), color='red')
                log_to_blender("✅ PIL test successful")
            except Exception as e:
                log_to_blender(f"❌ PIL test failed: {e}")
                raise
            
            # Overall status
            status = "All bundled dependencies working perfectly"
            self.report({'INFO'}, status)
            log_to_blender(f"Overall status: {status}")
            
        except ImportError as e:
            log_to_blender(f"❌ CRITICAL: Missing bundled dependencies: {e}")
            log_to_blender("This addon requires bundled dependencies in the lib/ folder")
            log_to_blender("Please download a properly bundled version of the addon")
            self.report({'ERROR'}, "Missing bundled dependencies - download bundled version")
            return {'CANCELLED'}
        except Exception as e:
            log_to_blender(f"❌ Dependency test failed: {e}")
            self.report({'ERROR'}, f"Dependency test failed: {e}")
            return {'CANCELLED'}
        
        log_to_blender("=== BUNDLED DEPENDENCY TEST COMPLETE ===")
        return {'FINISHED'}


classes = [
    RUNCHAT_OT_test_api_connection,
    RUNCHAT_OT_open_info_log,
    RUNCHAT_OT_clear_workflow,
    RUNCHAT_OT_test_dependencies,
] 