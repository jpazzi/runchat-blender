# __init__.py
# Runchat Blender Addon - Integrates Runchat workflows directly into Blender
# Copyright (C) 2024 Runchat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# This plugin connects to the Runchat API, which is a separate service
# with its own terms of service and privacy policy.

# Wheel-based dependencies are automatically handled by Blender's extension system
# No manual path manipulation needed for wheel-based dependencies

bl_info = {
    "name": "Runchat Blender Addon",
    "author": "Runchat",
    "version": (1, 2, 0), 
    "blender": (3, 0, 0),
    "location": "Properties > Scene Properties > Runchat",
    "description": "Integrates Runchat workflows directly into Blender",
    "warning": "",
    "doc_url": "https://docs.runchat.app",
    "category": "System",
    "license": "GPL v3",
}

import bpy

# Import modules in a way that allows for easy reloading
from . import api
from . import utils
from . import preferences
from . import properties
from . import operators
from . import ui

# List of modules to reload for development
modules = [
    api,
    utils,
    preferences,
    properties,
    operators,
    ui,
]

def register():
    """Registers the addon's classes and properties."""
    # Register in the correct order:
    # 1. Preferences
    # 2. Properties (data structures)
    # 3. Operators (actions)
    # 4. UI (panels)
    
    try:
        print("Registering Runchat Addon...")
        
        preferences.register()
        print("✓ Preferences registered")
        
        properties.register()
        print("✓ Properties registered")
        
        operators.register()
        print("✓ Operators registered")
        
        ui.register()
        print("✓ UI registered")
        
        # Add the main property group to Blender's Scene type
        bpy.types.Scene.runchat_properties = bpy.props.PointerProperty(type=properties.RunChatProperties)
        print("✓ Property group attached to Scene")
        
        print("✅ Runchat Addon Registered Successfully")
        
        # Auto-load examples after a short delay to avoid blocking startup
        def load_examples_delayed():
            try:
                print("Auto-loading workflow examples...")
                bpy.ops.runchat.load_examples()
            except Exception as e:
                print(f"Failed to auto-load examples: {e}")
            # Don't repeat the timer
            return None
        
        # Register timer to load examples after 2 seconds
        bpy.app.timers.register(load_examples_delayed, first_interval=2.0)
        
    except Exception as e:
        print(f"❌ Error during Runchat addon registration: {e}")
        import traceback
        print(traceback.format_exc())
        raise

def unregister():
    """Unregisters the addon's classes and properties."""
    # Unregister in reverse order to avoid dependency issues
    
    try:
        print("Unregistering Runchat Addon...")
        
        # Remove the main property group from the Scene
        if hasattr(bpy.types.Scene, 'runchat_properties'):
            del bpy.types.Scene.runchat_properties
            print("✓ Property group removed from Scene")
        
        ui.unregister()
        print("✓ UI unregistered")
        
        operators.unregister()
        print("✓ Operators unregistered")
        
        properties.unregister()
        print("✓ Properties unregistered")
        
        preferences.unregister()
        print("✓ Preferences unregistered")
        
        print("✅ Runchat Addon Unregistered Successfully")
        
    except Exception as e:
        print(f"❌ Error during Runchat addon unregistration: {e}")
        import traceback
        print(traceback.format_exc())

# This allows for reloading the script for development
if __name__ == "__main__":
    register()