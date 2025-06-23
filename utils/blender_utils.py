# utils/blender_utils.py

import bpy
from typing import Any, Dict, Callable


def get_blender_version_info() -> Dict[str, Any]:
    """Get detailed Blender version information"""
    try:
        version = bpy.app.version
        return {
            'version': f"{version[0]}.{version[1]}.{version[2]}",
            'version_string': bpy.app.version_string,
            'build_date': bpy.app.build_date.decode('utf-8') if hasattr(bpy.app.build_date, 'decode') else str(bpy.app.build_date),
            'build_hash': bpy.app.build_hash.decode('utf-8') if hasattr(bpy.app.build_hash, 'decode') else str(bpy.app.build_hash),
            'build_platform': bpy.app.build_platform.decode('utf-8') if hasattr(bpy.app.build_platform, 'decode') else str(bpy.app.build_platform),
            'major': version[0],
            'minor': version[1],
            'patch': version[2]
        }
    except Exception as e:
        print(f"Error getting Blender version info: {e}")
        return {
            'version': 'unknown',
            'version_string': 'unknown',
            'error': str(e)
        }


def create_progress_callback(node, operation_name: str) -> Callable:
    """Create a progress callback function for long operations"""
    def update_progress(progress: float, message: str = ""):
        """Update progress display in Blender UI"""
        try:
            # Update window manager progress if available
            if hasattr(bpy.context, 'window_manager'):
                wm = bpy.context.window_manager
                if hasattr(wm, 'progress_update'):
                    wm.progress_update(progress)
            
            # Print progress for console users
            if message:
                print(f"{operation_name}: {progress:.1%} - {message}")
            else:
                print(f"{operation_name}: {progress:.1%}")
                
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    return update_progress


def safe_scene_update():
    """Safely update the scene and UI"""
    try:
        # Update scene
        if hasattr(bpy.context, 'scene'):
            bpy.context.scene.update()
        
        # Update view layer
        if hasattr(bpy.context, 'view_layer'):
            bpy.context.view_layer.update()
        
        # Force UI redraw
        for area in bpy.context.screen.areas:
            area.tag_redraw()
            
    except Exception as e:
        print(f"Error updating scene: {e}")


def get_active_object_info() -> Dict[str, Any]:
    """Get information about the active object"""
    try:
        obj = bpy.context.active_object
        if not obj:
            return {'active': False}
        
        return {
            'active': True,
            'name': obj.name,
            'type': obj.type,
            'location': list(obj.location),
            'rotation': list(obj.rotation_euler),
            'scale': list(obj.scale),
            'visible': obj.visible_get(),
            'selected': obj.select_get()
        }
        
    except Exception as e:
        print(f"Error getting active object info: {e}")
        return {'active': False, 'error': str(e)}


def get_scene_info() -> Dict[str, Any]:
    """Get information about the current scene"""
    try:
        scene = bpy.context.scene
        
        return {
            'name': scene.name,
            'frame_current': scene.frame_current,
            'frame_start': scene.frame_start,
            'frame_end': scene.frame_end,
            'render_width': scene.render.resolution_x,
            'render_height': scene.render.resolution_y,
            'render_fps': scene.render.fps,
            'object_count': len(scene.objects),
            'selected_count': len(bpy.context.selected_objects)
        }
        
    except Exception as e:
        print(f"Error getting scene info: {e}")
        return {'error': str(e)}


def safe_operator_call(operator_name: str, **kwargs) -> bool:
    """Safely call a Blender operator with error handling"""
    try:
        # Get the operator
        op_parts = operator_name.split('.')
        if len(op_parts) != 2:
            print(f"Invalid operator name format: {operator_name}")
            return False
        
        module_name, op_name = op_parts
        
        if not hasattr(bpy.ops, module_name):
            print(f"Operator module not found: {module_name}")
            return False
        
        module = getattr(bpy.ops, module_name)
        if not hasattr(module, op_name):
            print(f"Operator not found: {op_name}")
            return False
        
        operator = getattr(module, op_name)
        
        # Call the operator
        result = operator(**kwargs)
        
        return result == {'FINISHED'}
        
    except Exception as e:
        print(f"Error calling operator {operator_name}: {e}")
        return False


def ensure_object_mode():
    """Ensure we're in Object mode"""
    try:
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        return True
    except Exception as e:
        print(f"Error setting object mode: {e}")
        return False


def clear_scene_safely():
    """Safely clear the current scene"""
    try:
        # Ensure object mode
        ensure_object_mode()
        
        # Select all objects
        bpy.ops.object.select_all(action='SELECT')
        
        # Delete selected objects
        bpy.ops.object.delete(use_global=False)
        
        # Clear orphaned data
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)
        
        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)
        
        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)
        
        print("Scene cleared successfully")
        return True
        
    except Exception as e:
        print(f"Error clearing scene: {e}")
        return False


def create_collection(name: str, parent=None) -> bpy.types.Collection:
    """Create a new collection with optional parent"""
    try:
        # Check if collection already exists
        if name in bpy.data.collections:
            return bpy.data.collections[name]
        
        # Create new collection
        collection = bpy.data.collections.new(name)
        
        # Link to parent or scene
        if parent and hasattr(parent, 'children'):
            parent.children.link(collection)
        else:
            bpy.context.scene.collection.children.link(collection)
        
        print(f"Created collection: {name}")
        return collection
        
    except Exception as e:
        print(f"Error creating collection: {e}")
        return None


def move_object_to_collection(obj, collection_name: str):
    """Move an object to a specific collection"""
    try:
        if not obj:
            return False
        
        # Get or create the target collection
        if collection_name in bpy.data.collections:
            target_collection = bpy.data.collections[collection_name]
        else:
            target_collection = create_collection(collection_name)
        
        if not target_collection:
            return False
        
        # Unlink from all current collections
        for collection in obj.users_collection:
            collection.objects.unlink(obj)
        
        # Link to target collection
        target_collection.objects.link(obj)
        
        print(f"Moved {obj.name} to collection {collection_name}")
        return True
        
    except Exception as e:
        print(f"Error moving object to collection: {e}")
        return False


def get_addon_preferences():
    """Get the addon preferences"""
    try:
        addon_name = __name__.split('.')[0]  # Get the main addon name
        if addon_name in bpy.context.preferences.addons:
            return bpy.context.preferences.addons[addon_name].preferences
        return None
    except Exception as e:
        print(f"Error getting addon preferences: {e}")
        return None


def is_valid_context_for_operation(required_mode: str = None) -> bool:
    """Check if the current context is valid for an operation"""
    try:
        # Check if we have a valid context
        if not hasattr(bpy.context, 'scene'):
            return False
        
        # Check mode if specified
        if required_mode and bpy.context.mode != required_mode:
            return False
        
        # Check for active object if needed
        if required_mode and 'EDIT' in required_mode and not bpy.context.active_object:
            return False
        
        return True
        
    except Exception as e:
        print(f"Error checking context validity: {e}")
        return False


def force_ui_update():
    """Force a complete UI update"""
    try:
        # Update all areas
        for area in bpy.context.screen.areas:
            area.tag_redraw()
        
        # Update scene
        if hasattr(bpy.context, 'scene'):
            safe_scene_update()
        
        # Process events
        if hasattr(bpy.app, 'handlers'):
            for handler_list in bpy.app.handlers.__dict__.values():
                if isinstance(handler_list, list):
                    for handler in handler_list:
                        try:
                            if callable(handler):
                                handler()
                        except:
                            pass  # Ignore handler errors
        
        return True
        
    except Exception as e:
        print(f"Error forcing UI update: {e}")
        return False 