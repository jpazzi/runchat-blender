bl_info = {
    "name": "RunChat Blender Nodes",
    "author": "RunChat Integration",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Shader Editor > Add > RunChat",
    "description": "Custom nodes for interfacing with RunChat workflows",
    "warning": "",
    "doc_url": "https://docs.runchat.app",
    "category": "Node",
}

import bpy
from . import runchat_nodes
from . import preferences

def register():
    preferences.register()
    runchat_nodes.register()

def unregister():
    runchat_nodes.unregister()
    preferences.unregister()

if __name__ == "__main__":
    register() 