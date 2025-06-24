# operators/__init__.py

from . import schema
from . import execution
from . import capture
from . import media
from . import upload  
from . import utils
from . import debug

# Collect all classes from submodules
classes = []
classes.extend(schema.classes)
classes.extend(execution.classes)
classes.extend(capture.classes)
classes.extend(media.classes)
classes.extend(upload.classes)
classes.extend(utils.classes)
classes.extend(debug.classes)

def register():
    """Register all operator classes"""
    import bpy
    
    # Execution operators
    bpy.utils.register_class(execution.RUNCHAT_OT_execute)

    
    # Schema operators
    bpy.utils.register_class(schema.RUNCHAT_OT_load_schema)
    bpy.utils.register_class(schema.RUNCHAT_OT_load_examples)
    bpy.utils.register_class(schema.RUNCHAT_OT_use_example)
    
    # Capture operators
    bpy.utils.register_class(capture.RUNCHAT_OT_preview_viewport)
    bpy.utils.register_class(capture.RUNCHAT_OT_upload_viewport)
    bpy.utils.register_class(capture.RUNCHAT_OT_preview_image)
    
    # Upload operations
    bpy.utils.register_class(upload.RUNCHAT_OT_upload_file)
    
    # Media operations  
    bpy.utils.register_class(media.RUNCHAT_OT_view_image)
    bpy.utils.register_class(media.RUNCHAT_OT_save_image)
    bpy.utils.register_class(media.RUNCHAT_OT_popup_image_viewer)
    bpy.utils.register_class(media.RUNCHAT_OT_open_image_editor)
    bpy.utils.register_class(media.RUNCHAT_OT_save_image_as)
    bpy.utils.register_class(media.RUNCHAT_OT_open_video_editor)
    bpy.utils.register_class(media.RUNCHAT_OT_open_video)
    bpy.utils.register_class(media.RUNCHAT_OT_save_video)
    bpy.utils.register_class(media.RUNCHAT_OT_import_model)
    bpy.utils.register_class(media.RUNCHAT_OT_save_model)
    bpy.utils.register_class(media.RUNCHAT_OT_import_video)
    
    # Utility operations
    bpy.utils.register_class(utils.RUNCHAT_OT_copy_text)
    bpy.utils.register_class(utils.RUNCHAT_OT_open_editor)
    bpy.utils.register_class(utils.RUNCHAT_OT_help)
    bpy.utils.register_class(utils.RUNCHAT_OT_open_link)
    
    # Debug operators
    bpy.utils.register_class(debug.RUNCHAT_OT_test_api_connection)
    bpy.utils.register_class(debug.RUNCHAT_OT_open_info_log)
    bpy.utils.register_class(debug.RUNCHAT_OT_clear_workflow)

def unregister():
    """Unregister all operator classes"""
    import bpy
    
    # Debug operators
    bpy.utils.unregister_class(debug.RUNCHAT_OT_clear_workflow)
    bpy.utils.unregister_class(debug.RUNCHAT_OT_open_info_log)
    bpy.utils.unregister_class(debug.RUNCHAT_OT_test_api_connection)
    
    # Utility operations
    bpy.utils.unregister_class(utils.RUNCHAT_OT_open_link)
    bpy.utils.unregister_class(utils.RUNCHAT_OT_help)
    bpy.utils.unregister_class(utils.RUNCHAT_OT_open_editor)
    bpy.utils.unregister_class(utils.RUNCHAT_OT_copy_text)
    
    # Media operations
    bpy.utils.unregister_class(media.RUNCHAT_OT_import_video)
    bpy.utils.unregister_class(media.RUNCHAT_OT_save_model)
    bpy.utils.unregister_class(media.RUNCHAT_OT_import_model)
    bpy.utils.unregister_class(media.RUNCHAT_OT_save_video)
    bpy.utils.unregister_class(media.RUNCHAT_OT_open_video)
    bpy.utils.unregister_class(media.RUNCHAT_OT_open_video_editor)
    bpy.utils.unregister_class(media.RUNCHAT_OT_save_image_as)
    bpy.utils.unregister_class(media.RUNCHAT_OT_open_image_editor)
    bpy.utils.unregister_class(media.RUNCHAT_OT_popup_image_viewer)
    bpy.utils.unregister_class(media.RUNCHAT_OT_save_image)
    bpy.utils.unregister_class(media.RUNCHAT_OT_view_image)
    
    # Upload operations
    bpy.utils.unregister_class(upload.RUNCHAT_OT_upload_file)
    
    # Capture operators
    bpy.utils.unregister_class(capture.RUNCHAT_OT_preview_image)
    bpy.utils.unregister_class(capture.RUNCHAT_OT_upload_viewport)
    bpy.utils.unregister_class(capture.RUNCHAT_OT_preview_viewport)
    
    # Schema operators
    bpy.utils.unregister_class(schema.RUNCHAT_OT_use_example)
    bpy.utils.unregister_class(schema.RUNCHAT_OT_load_examples)
    bpy.utils.unregister_class(schema.RUNCHAT_OT_load_schema)
    
    # Execution operators

    bpy.utils.unregister_class(execution.RUNCHAT_OT_execute) 