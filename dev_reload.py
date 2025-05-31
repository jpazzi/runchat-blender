"""
RunChat Addon Development Hot Reload Script

Save this script in Blender's Text Editor and run it whenever you make changes
to the addon code. This will reload all addon modules without requiring a restart.

Usage:
1. Open Blender Text Editor
2. Create new text or open this file
3. Run script (Alt+P or click Run button)
4. Your addon changes will be applied immediately

For automatic reload on file changes, you can also use external tools like:
- watchdog with Python file monitoring
- VS Code with Blender addon development extensions
"""

import bpy
import importlib
import sys
import os

def hot_reload_runchat_addon():
    """Hot reload all RunChat addon modules"""
    
    print("=" * 50)
    print("🔄 RunChat Addon Hot Reload")
    print("=" * 50)
    
    try:
        # Determine addon name (adjust if your addon has a different name)
        addon_names = ['runchat_blender', 'runchat']
        addon_name = None
        
        # Find the correct addon name
        for name in addon_names:
            if name in bpy.context.preferences.addons:
                addon_name = name
                break
        
        if not addon_name:
            print("❌ RunChat addon not found in enabled addons")
            print("   Make sure the addon is enabled first")
            return False
        
        print(f"📦 Found addon: {addon_name}")
        
        # Find all modules belonging to this addon
        addon_modules = []
        for module_name in list(sys.modules.keys()):
            if module_name.startswith(addon_name):
                addon_modules.append(module_name)
        
        if not addon_modules:
            print("❌ No addon modules found to reload")
            return False
        
        print(f"🔍 Found {len(addon_modules)} modules to reload:")
        for module in addon_modules:
            print(f"   • {module}")
        
        # Reload modules in reverse order (dependencies first)
        reloaded_count = 0
        failed_count = 0
        
        for module_name in reversed(addon_modules):
            if module_name in sys.modules:
                try:
                    importlib.reload(sys.modules[module_name])
                    reloaded_count += 1
                    print(f"   ✅ Reloaded: {module_name}")
                except Exception as e:
                    failed_count += 1
                    print(f"   ❌ Failed: {module_name} - {str(e)}")
        
        print("-" * 50)
        print(f"✨ Hot reload complete!")
        print(f"   Reloaded: {reloaded_count} modules")
        if failed_count > 0:
            print(f"   Failed: {failed_count} modules")
        
        # Refresh node editor if open
        try:
            for area in bpy.context.screen.areas:
                if area.type == 'NODE_EDITOR':
                    area.tag_redraw()
            print("🔄 Node editor refreshed")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"💥 Hot reload failed: {str(e)}")
        return False

def full_addon_restart():
    """Completely restart the addon (disable/enable cycle)"""
    
    print("=" * 50)
    print("🔄 RunChat Addon Full Restart")
    print("=" * 50)
    
    try:
        addon_names = ['runchat_blender', 'runchat']
        addon_name = None
        
        for name in addon_names:
            if name in bpy.context.preferences.addons:
                addon_name = name
                break
        
        if not addon_name:
            print("❌ Addon not found")
            return False
        
        print(f"📦 Restarting addon: {addon_name}")
        
        # Disable addon
        bpy.ops.preferences.addon_disable(module=addon_name)
        print("   ⏹️ Addon disabled")
        
        # Enable addon
        bpy.ops.preferences.addon_enable(module=addon_name)
        print("   ▶️ Addon enabled")
        
        print("✨ Full restart complete!")
        return True
        
    except Exception as e:
        print(f"💥 Restart failed: {str(e)}")
        return False

def check_addon_status():
    """Check the current status of the RunChat addon"""
    
    print("=" * 50)
    print("📊 RunChat Addon Status")
    print("=" * 50)
    
    addon_names = ['runchat_blender', 'runchat']
    found_addon = False
    
    for name in addon_names:
        if name in bpy.context.preferences.addons:
            found_addon = True
            addon = bpy.context.preferences.addons[name]
            print(f"✅ Addon '{name}' is enabled")
            
            # Check if development mode is available
            if hasattr(addon.preferences, 'development_mode'):
                dev_mode = addon.preferences.development_mode
                print(f"🛠️ Development mode: {'ON' if dev_mode else 'OFF'}")
            
            # Count loaded modules
            module_count = len([m for m in sys.modules.keys() if m.startswith(name)])
            print(f"📦 Loaded modules: {module_count}")
    
    if not found_addon:
        print("❌ RunChat addon not found or not enabled")
        print("   Available addons:")
        for addon_name in bpy.context.preferences.addons.keys():
            if 'runchat' in addon_name.lower():
                print(f"     • {addon_name}")

# Main execution
if __name__ == "__main__":
    print("\n🚀 RunChat Development Helper")
    print("Choose an action:")
    print("1. Hot reload (fast, preserves state)")
    print("2. Full restart (slow, fresh state)")  
    print("3. Check addon status")
    
    # For script execution, default to hot reload
    # You can modify this or create separate scripts for each action
    
    # Uncomment the action you want:
    hot_reload_runchat_addon()        # Hot reload (recommended for development)
    # full_addon_restart()           # Full restart
    # check_addon_status()           # Status check

    print("\n💡 Tip: Enable 'Development Mode' in addon preferences for GUI reload buttons!") 