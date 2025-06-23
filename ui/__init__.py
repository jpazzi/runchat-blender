# ui/__init__.py

from . import panels
from . import helpers

# Collect all classes from submodules
classes = []
classes.extend(panels.classes)

def register():
    """Register all UI classes"""
    import bpy
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister all UI classes"""
    import bpy
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls) 