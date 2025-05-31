import bpy
import nodeitems_utils
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty
import requests
import json
import threading
import base64
import os
import tempfile
import time
from . import preferences
from . import utils

# Custom node tree for RunChat nodes
class RunChatNodeTree(NodeTree):
    bl_idname = 'RunChatNodeTree'
    bl_label = "RunChat Nodes"
    bl_icon = 'NODETREE'

# Custom socket types
class RunChatImageSocket(NodeSocket):
    bl_idname = 'RunChatImageSocket'
    bl_label = "RunChat Image Socket"
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (1.0, 0.8, 0.2, 1.0)  # Orange color for image sockets

class RunChatModelSocket(NodeSocket):
    bl_idname = 'RunChatModelSocket'
    bl_label = "RunChat Model Socket"
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (0.2, 0.8, 1.0, 1.0)  # Blue color for model sockets

class RunChatDataSocket(NodeSocket):
    bl_idname = 'RunChatDataSocket'
    bl_label = "RunChat Data Socket"
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (0.8, 0.8, 0.8, 1.0)  # Gray color for generic data

class RunChatWebhookSocket(NodeSocket):
    bl_idname = 'RunChatWebhookSocket'
    bl_label = "RunChat Webhook Socket"
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (0.8, 0.2, 1.0, 1.0)  # Purple color for webhook data

# Base RunChat Node
class RunChatNodeBase(Node):
    bl_label = "RunChat Base Node"
    
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'RunChatNodeTree'

# Main RunChat Executor Node
class RunChatExecutorNode(RunChatNodeBase):
    bl_idname = 'RunChatExecutorNode'
    bl_label = "RunChat Executor"
    bl_icon = 'MESH_MONKEY'
    
    # Properties
    workflow_id: StringProperty(
        name="Workflow ID",
        description="RunChat workflow ID from the editor URL",
        default=""
    )
    
    auto_execute: BoolProperty(
        name="Auto Execute",
        description="Automatically execute when inputs change",
        default=False
    )
    
    status: StringProperty(
        name="Status",
        description="Current execution status",
        default="Ready"
    )
    
    instance_id: StringProperty(
        name="Instance ID",
        description="RunChat instance ID for maintaining state",
        default=""
    )
    
    schema_loaded: BoolProperty(
        name="Schema Loaded",
        description="Whether the workflow schema has been loaded",
        default=False
    )
    
    execution_time: FloatProperty(
        name="Execution Time",
        description="Last execution time in seconds",
        default=0.0
    )
    
    use_webhook_mode: BoolProperty(
        name="Webhook Mode",
        description="Send raw data to webhook instead of using schema",
        default=False
    )
    
    # Store schema data
    schema_data: StringProperty(
        name="Schema Data",
        description="Cached schema JSON",
        default=""
    )
    
    # Add loading state tracking
    is_loading: BoolProperty(
        name="Is Loading",
        description="Whether a request is currently in progress",
        default=False
    )
    
    def init(self, context):
        # Default output setup - no workflow ID input needed since we have the property
        self.outputs.new('RunChatDataSocket', "Output")
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        
        # Workflow ID input
        if not self.schema_loaded:
            col.prop(self, "workflow_id", text="Workflow ID")
            if not self.is_loading:
                col.operator("runchat.load_schema", text="Load Schema").node_name = self.name
            else:
                row = col.row()
                row.operator("runchat.cancel_loading", text="Cancel", icon='X').node_name = self.name
                row.enabled = True
        else:
            row = col.row()
            row.prop(self, "workflow_id", text="ID")
            row.operator("runchat.reload_schema", text="Reload").node_name = self.name
        
        # Mode selection
        col.separator()
        col.prop(self, "use_webhook_mode", text="Webhook Mode")
        
        # Execution controls
        col.separator()
        if self.schema_loaded or self.use_webhook_mode:
            col.operator("runchat.execute", text="Execute").node_name = self.name
            col.prop(self, "auto_execute")
        
        # Status and metrics display
        col.separator()
        if self.is_loading:
            row = col.row()
            row.alert = True
            row.label(text=f"⏳ {self.status}", icon='TIME')
        else:
            col.label(text=f"Status: {self.status}")
            
        if self.execution_time > 0:
            col.label(text=f"Last execution: {self.execution_time:.2f}s")
        
        # Instance management
        if self.instance_id:
            col.separator()
            col.label(text=f"Instance: {self.instance_id[:8]}...")
            col.operator("runchat.clear_instance", text="New Instance").node_name = self.name
        
        # Utility buttons
        col.separator()
        row = col.row()
        row.operator("runchat.open_editor", text="Edit").workflow_id = self.workflow_id
        row.operator("runchat.copy_id", text="Copy ID").workflow_id = self.workflow_id
    
    def update(self):
        if self.auto_execute and (self.schema_loaded or self.use_webhook_mode):
            # Trigger execution when inputs change
            bpy.ops.runchat.execute(node_name=self.name)

# Image Send Node
class RunChatImageSendNode(RunChatNodeBase):
    bl_idname = 'RunChatImageSendNode'
    bl_label = "RunChat Image Send"
    bl_icon = 'IMAGE_DATA'
    
    image_path: StringProperty(
        name="Image Path",
        description="Path to the image file to send",
        default="",
        subtype='FILE_PATH'
    )
    
    use_render_result: BoolProperty(
        name="Use Render Result",
        description="Send the current render result instead of file",
        default=False
    )
    
    use_active_image: BoolProperty(
        name="Use Active Image",
        description="Send the active image in the UV/Image Editor",
        default=False
    )
    
    compression_quality: IntProperty(
        name="Quality",
        description="JPEG compression quality (0-100)",
        default=90,
        min=0,
        max=100
    )
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "Image Path")
        self.outputs.new('RunChatImageSocket', "Image Data")
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        
        # Source selection
        col.prop(self, "use_render_result")
        col.prop(self, "use_active_image")
        
        if not self.use_render_result and not self.use_active_image:
            col.prop(self, "image_path", text="")
        
        col.prop(self, "compression_quality")
        
        # Show PIL status
        if not utils.PIL_AVAILABLE:
            row = col.row()
            row.alert = True
            row.label(text="⚠️ No compression (PIL missing)", icon='ERROR')
        
        col.operator("runchat.send_image", text="Process Image").node_name = self.name

# Image Receive Node  
class RunChatImageReceiveNode(RunChatNodeBase):
    bl_idname = 'RunChatImageReceiveNode'
    bl_label = "RunChat Image Receive"
    bl_icon = 'IMAGE_DATA'
    
    save_path: StringProperty(
        name="Save Path",
        description="Directory to save received images",
        default="//images/",
        subtype='DIR_PATH'
    )
    
    auto_save: BoolProperty(
        name="Auto Save",
        description="Automatically save images when received",
        default=True
    )
    
    load_to_blender: BoolProperty(
        name="Load to Blender",
        description="Load received images into Blender's image editor",
        default=True
    )
    
    create_material: BoolProperty(
        name="Create Material",
        description="Create a material with the received image",
        default=False
    )
    
    def init(self, context):
        self.inputs.new('RunChatImageSocket', "Image Data")
        self.outputs.new('NodeSocketString', "File Path")
        self.outputs.new('NodeSocketShader', "Material")
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "save_path", text="Save To")
        col.prop(self, "auto_save")
        col.prop(self, "load_to_blender")
        col.prop(self, "create_material")
        col.operator("runchat.receive_image", text="Process Image").node_name = self.name

# 3D Model URL Loader Node
class RunChatModelLoaderNode(RunChatNodeBase):
    bl_idname = 'RunChatModelLoaderNode'
    bl_label = "RunChat Model Loader"
    bl_icon = 'MESH_CUBE'
    
    model_url: StringProperty(
        name="Model URL",
        description="URL to download the 3D model from",
        default=""
    )
    
    import_format: EnumProperty(
        name="Format",
        description="Expected model format",
        items=[
            ('AUTO', "Auto Detect", "Automatically detect format from URL"),
            ('OBJ', "OBJ", "Wavefront OBJ format"),
            ('FBX', "FBX", "Autodesk FBX format"),
            ('PLY', "PLY", "Stanford PLY format"),
            ('STL', "STL", "STereoLithography format"),
            ('GLTF', "glTF", "GL Transmission Format"),
            ('BLEND', "Blend", "Blender file format"),
        ],
        default='AUTO'
    )
    
    import_scale: FloatProperty(
        name="Import Scale",
        description="Scale factor for imported model",
        default=1.0,
        min=0.001,
        max=1000.0
    )
    
    clear_scene: BoolProperty(
        name="Clear Scene",
        description="Clear existing objects before importing",
        default=False
    )
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "Model URL")
        self.outputs.new('RunChatModelSocket', "Model Data")
        self.outputs.new('NodeSocketGeometry', "Geometry")
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "model_url", text="URL")
        col.prop(self, "import_format", text="Format")
        col.prop(self, "import_scale")
        col.prop(self, "clear_scene")
        col.operator("runchat.load_model", text="Load Model").node_name = self.name

# Webhook Data Node
class RunChatWebhookNode(RunChatNodeBase):
    bl_idname = 'RunChatWebhookNode'
    bl_label = "RunChat Webhook Data"
    bl_icon = 'WORLD_DATA'
    
    webhook_data: StringProperty(
        name="Webhook Data",
        description="JSON data to send to webhook",
        default="{}",
        subtype='PASSWORD'  # Hide long JSON strings
    )
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "JSON Data")
        self.outputs.new('RunChatWebhookSocket', "Webhook Data")
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "webhook_data", text="JSON")
        col.operator("runchat.validate_json", text="Validate JSON").node_name = self.name
        col.operator("runchat.format_json", text="Format JSON").node_name = self.name

# Enhanced operators with better error handling and API integration
class RUNCHAT_OT_LoadSchema(bpy.types.Operator):
    """Load workflow schema from RunChat"""
    bl_idname = "runchat.load_schema"
    bl_label = "Load Schema"
    
    node_name: StringProperty()
    
    def execute(self, context):
        node = self.get_node(context)
        if not node:
            return {'CANCELLED'}
        
        if not utils.validate_workflow_id(node.workflow_id):
            self.report({'ERROR'}, "Invalid workflow ID format")
            return {'CANCELLED'}
        
        if node.is_loading:
            self.report({'WARNING'}, "Already loading schema...")
            return {'CANCELLED'}
        
        # Start async schema loading
        node.is_loading = True
        threading.Thread(target=self.load_schema_async, args=(node,)).start()
        node.status = "Loading schema..."
        
        return {'FINISHED'}
    
    def get_node(self, context):
        """Get node from context with better error handling"""
        try:
            if hasattr(context, 'node_tree') and context.node_tree:
                return context.node_tree.nodes.get(self.node_name)
            
            # Fallback: search all node trees
            for node_tree in bpy.data.node_groups:
                if node_tree.bl_idname == 'RunChatNodeTree':
                    node = node_tree.nodes.get(self.node_name)
                    if node:
                        return node
            
            self.report({'ERROR'}, "Node not found")
            return None
        except Exception as e:
            self.report({'ERROR'}, f"Error finding node: {str(e)}")
            return None
    
    def load_schema_async(self, node):
        node_name = node.name  # Store node name instead of reference
        node_tree_name = None
        
        # Find the node tree name
        for tree in bpy.data.node_groups:
            if tree.bl_idname == 'RunChatNodeTree' and node_name in tree.nodes:
                node_tree_name = tree.name
                break
        
        if not node_tree_name:
            print("❌ Could not find node tree for async operation")
            return
            
        try:
            url = f"https://runchat.app/api/v1/{node.workflow_id}/schema"
            headers = {'Authorization': f'Bearer {preferences.get_api_key()}'}
            
            # Debug output
            print(f"🔄 Loading schema for workflow: {node.workflow_id}")
            print(f"🌐 URL: {url}")
            print(f"🔑 API key present: {'Yes' if preferences.get_api_key() else 'No'}")
            
            # Update status with more detail - using safe node access
            def update_status(msg):
                try:
                    tree = bpy.data.node_groups.get(node_tree_name)
                    if tree and node_name in tree.nodes:
                        tree.nodes[node_name].status = msg
                        print(f"📊 Status: {msg}")
                except:
                    print(f"📊 Status (node unavailable): {msg}")
            
            bpy.app.timers.register(lambda: update_status("Connecting to RunChat API..."), first_interval=0.1)
            
            print("🌐 Making HTTP request...")
            response = requests.get(url, headers=headers, timeout=60)  # Increased timeout
            print(f"📥 Response received: {response.status_code}")
            print(f"📦 Response size: {len(response.content)} bytes")
            print(f"📋 Response headers: {dict(response.headers)}")
            
            bpy.app.timers.register(lambda: update_status("Checking response status..."), first_interval=0.1)
            
            print("✅ Checking response status...")
            response.raise_for_status()
            print("✅ Response status OK")
            
            bpy.app.timers.register(lambda: update_status("Parsing JSON response..."), first_interval=0.1)
            
            print("📄 Parsing JSON...")
            schema = response.json()
            print(f"✅ JSON parsed successfully")
            print(f"📊 Schema keys: {list(schema.keys()) if isinstance(schema, dict) else 'Not a dict'}")
            print(f"✅ Schema loaded successfully: {len(schema.get('inputs', []))} inputs, {len(schema.get('outputs', []))} outputs")
            
            bpy.app.timers.register(lambda: update_status("Caching schema data..."), first_interval=0.1)
            
            # Cache the schema with safety checks
            print("💾 Caching schema data...")
            print(f"📊 Schema type: {type(schema)}")
            print(f"📊 Schema size estimate: {len(str(schema))} chars")
            
            schema_data = None
            try:
                # Try to serialize with a size limit check first
                schema_str = str(schema)
                if len(schema_str) > 1000000:  # 1MB limit
                    print(f"⚠️ Schema very large ({len(schema_str)} chars), truncating for cache...")
                    # Store a minimal version for caching
                    minimal_schema = {
                        'inputs': schema.get('inputs', []),
                        'outputs': schema.get('outputs', []),
                        '_truncated': True,
                        '_original_size': len(schema_str)
                    }
                    schema_data = json.dumps(minimal_schema)
                    print("✅ Minimal schema cached")
                else:
                    # Try normal caching
                    print("🔄 Attempting full schema serialization...")
                    schema_data = json.dumps(schema)
                    print("✅ Full schema cached")
                    
            except Exception as cache_error:
                print(f"❌ Schema caching failed: {cache_error}")
                # Store minimal working data
                minimal_schema = {
                    'inputs': schema.get('inputs', [])[:50],  # Limit inputs
                    'outputs': schema.get('outputs', [])[:50],  # Limit outputs  
                    '_cache_error': str(cache_error),
                    '_fallback': True
                }
                try:
                    schema_data = json.dumps(minimal_schema)
                    print("✅ Fallback schema cached")
                except:
                    schema_data = '{"inputs":[], "outputs":[], "_error": "caching_failed"}'
                    print("✅ Emergency minimal schema cached")
            
            # Update node on main thread using safe node access
            print("🔄 Scheduling node update...")
            def update_node():
                print("🎯 Updating node schema...")
                try:
                    # Safely get the node reference
                    tree = bpy.data.node_groups.get(node_tree_name)
                    if not tree:
                        print("❌ Node tree no longer exists")
                        return
                        
                    target_node = tree.nodes.get(node_name)
                    if not target_node:
                        print("❌ Node no longer exists")
                        return
                    
                    # Store schema data safely
                    if schema_data:
                        target_node.schema_data = schema_data
                    
                    # Update node schema
                    self.update_node_schema(target_node, schema)
                    target_node.is_loading = False  # Clear loading state
                    print("✅ Node update complete")
                    
                except Exception as update_error:
                    print(f"❌ Node update failed: {update_error}")
                    # Try to at least clear the loading state
                    try:
                        tree = bpy.data.node_groups.get(node_tree_name)
                        if tree and node_name in tree.nodes:
                            tree.nodes[node_name].status = f"Update error: {str(update_error)[:50]}"
                            tree.nodes[node_name].is_loading = False
                    except:
                        pass
            
            bpy.app.timers.register(update_node, first_interval=0.1)
            print("✅ Update scheduled")
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
            def show_error():
                try:
                    tree = bpy.data.node_groups.get(node_tree_name)
                    if tree and node_name in tree.nodes:
                        target_node = tree.nodes[node_name]
                        if e.response.status_code == 401:
                            target_node.status = "Error: Invalid API key"
                        elif e.response.status_code == 404:
                            target_node.status = "Error: Workflow not found"
                        else:
                            target_node.status = f"Error: HTTP {e.response.status_code}"
                        target_node.is_loading = False
                except:
                    print("❌ Could not update node with HTTP error")
            
            bpy.app.timers.register(show_error, first_interval=0.1)
            
        except requests.exceptions.Timeout as e:
            print(f"⏰ Timeout Error: Request took longer than 60 seconds")
            def show_error():
                try:
                    tree = bpy.data.node_groups.get(node_tree_name)
                    if tree and node_name in tree.nodes:
                        tree.nodes[node_name].status = "Error: Request timeout (>60s)"
                        tree.nodes[node_name].is_loading = False
                except:
                    print("❌ Could not update node with timeout error")
            
            bpy.app.timers.register(show_error, first_interval=0.1)
            
        except requests.exceptions.ConnectionError as e:
            print(f"🌐 Connection Error: {str(e)}")
            def show_error():
                try:
                    tree = bpy.data.node_groups.get(node_tree_name)
                    if tree and node_name in tree.nodes:
                        tree.nodes[node_name].status = "Error: Connection failed"
                        tree.nodes[node_name].is_loading = False
                except:
                    print("❌ Could not update node with connection error")
            
            bpy.app.timers.register(show_error, first_interval=0.1)
            
        except json.JSONDecodeError as e:
            print(f"📄 JSON Decode Error: {str(e)}")
            print(f"📄 Response text preview: {response.text[:500]}...")
            def show_error():
                try:
                    tree = bpy.data.node_groups.get(node_tree_name)
                    if tree and node_name in tree.nodes:
                        tree.nodes[node_name].status = "Error: Invalid JSON response"
                        tree.nodes[node_name].is_loading = False
                except:
                    print("❌ Could not update node with JSON error")
            
            bpy.app.timers.register(show_error, first_interval=0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"🚨 Network Error: {str(e)}")
            def show_error():
                try:
                    tree = bpy.data.node_groups.get(node_tree_name)
                    if tree and node_name in tree.nodes:
                        tree.nodes[node_name].status = f"Network error: {str(e)[:50]}"
                        tree.nodes[node_name].is_loading = False
                except:
                    print("❌ Could not update node with network error")
            
            bpy.app.timers.register(show_error, first_interval=0.1)
            
        except Exception as e:
            print(f"💥 Unexpected Error: {str(e)}")
            import traceback
            print(f"🔍 Traceback: {traceback.format_exc()}")
            def show_error():
                try:
                    tree = bpy.data.node_groups.get(node_tree_name)
                    if tree and node_name in tree.nodes:
                        tree.nodes[node_name].status = f"Error: {str(e)[:50]}"
                        tree.nodes[node_name].is_loading = False
                except:
                    print("❌ Could not update node with general error")
            
            bpy.app.timers.register(show_error, first_interval=0.1)
    
    def update_node_schema(self, node, schema):
        try:
            # Clear existing dynamic sockets
            node.inputs.clear()
            
            # Clear outputs
            node.outputs.clear()
            
            # Add inputs based on schema with proper paramId_nodeId format
            if 'inputs' in schema:
                for input_def in schema['inputs']:
                    socket_type = self.get_socket_type(input_def.get('type', 'string'))
                    label = input_def.get('label', input_def.get('id', 'Input'))
                    socket = node.inputs.new(socket_type, label)
                    
                    # Store the full parameter info for API calls
                    socket['param_id'] = input_def.get('id', '')
                    socket['param_type'] = input_def.get('type', 'string')
                    socket['param_description'] = input_def.get('description', '')
                    
            # Add outputs based on schema
            if 'outputs' in schema:
                for output_def in schema['outputs']:
                    socket_type = self.get_socket_type(output_def.get('type', 'string'))
                    label = output_def.get('label', output_def.get('id', 'Output'))
                    socket = node.outputs.new(socket_type, label)
                    
                    socket['param_id'] = output_def.get('id', '')
                    socket['param_type'] = output_def.get('type', 'string')
            
            node.schema_loaded = True
            node.status = f"Schema loaded ({len(schema.get('inputs', []))} inputs, {len(schema.get('outputs', []))} outputs)"
            
        except Exception as e:
            node.status = f"Schema error: {str(e)}"
    
    def get_socket_type(self, data_type):
        """Map RunChat data types to Blender socket types"""
        type_mapping = {
            'image': 'RunChatImageSocket',
            'model': 'RunChatModelSocket',
            'webhook': 'RunChatWebhookSocket',
            'string': 'NodeSocketString',
            'float': 'NodeSocketFloat',
            'int': 'NodeSocketInt',
            'bool': 'NodeSocketBool',
            'vector': 'NodeSocketVector',
            'color': 'NodeSocketColor',
            'geometry': 'NodeSocketGeometry',
            'material': 'NodeSocketMaterial',
            'object': 'NodeSocketObject',
        }
        return type_mapping.get(data_type.lower(), 'RunChatDataSocket')

class RUNCHAT_OT_ReloadSchema(bpy.types.Operator):
    """Reload workflow schema"""
    bl_idname = "runchat.reload_schema"
    bl_label = "Reload Schema"
    
    node_name: StringProperty()
    
    def execute(self, context):
        node = context.scene.node_tree.nodes.get(self.node_name)
        if node:
            node.schema_loaded = False
            node.schema_data = ""
            node.is_loading = False
        
        return bpy.ops.runchat.load_schema(node_name=self.node_name)

class RUNCHAT_OT_CancelLoading(bpy.types.Operator):
    """Cancel schema loading"""
    bl_idname = "runchat.cancel_loading"
    bl_label = "Cancel Loading"
    
    node_name: StringProperty()
    
    def execute(self, context):
        # Find the node
        node = None
        for node_tree in bpy.data.node_groups:
            if node_tree.bl_idname == 'RunChatNodeTree':
                found_node = node_tree.nodes.get(self.node_name)
                if found_node:
                    node = found_node
                    break
        
        if node:
            node.is_loading = False
            node.status = "Loading cancelled"
            self.report({'INFO'}, "Loading cancelled")
        
        return {'FINISHED'}

class RUNCHAT_OT_Execute(bpy.types.Operator):
    """Execute RunChat workflow"""
    bl_idname = "runchat.execute"
    bl_label = "Execute Workflow"
    
    node_name: StringProperty()
    
    def execute(self, context):
        node = self.get_node(context)
        if not node:
            return {'CANCELLED'}
        
        if not (node.schema_loaded or node.use_webhook_mode):
            self.report({'ERROR'}, "Node not ready for execution. Load schema first or enable webhook mode.")
            return {'CANCELLED'}
        
        api_key = preferences.get_api_key()
        if not api_key:
            self.report({'ERROR'}, "API key not set. Check addon preferences.")
            return {'CANCELLED'}
        
        # Start async execution
        start_time = time.time()
        threading.Thread(target=self.execute_async, args=(node, api_key, start_time)).start()
        node.status = "Executing..."
        
        return {'FINISHED'}
    
    def get_node(self, context):
        """Get node with error handling"""
        try:
            if hasattr(context, 'node_tree') and context.node_tree:
                return context.node_tree.nodes.get(self.node_name)
            
            # Fallback search
            for node_tree in bpy.data.node_groups:
                if node_tree.bl_idname == 'RunChatNodeTree':
                    node = node_tree.nodes.get(self.node_name)
                    if node:
                        return node
            return None
        except:
            return None
    
    def execute_async(self, node, api_key, start_time):
        try:
            if node.use_webhook_mode:
                # Webhook mode: send raw data
                request_data = self.collect_webhook_data(node)
            else:
                # Schema mode: collect structured inputs
                request_data = self.collect_schema_inputs(node)
            
            url = f"https://runchat.app/api/v1/{node.workflow_id}"
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=request_data, headers=headers, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            execution_time = time.time() - start_time
            
            # Update node on main thread
            def update_results():
                self.update_node_results(node, result, execution_time)
            
            bpy.app.timers.register(update_results, first_interval=0.1)
            
        except requests.exceptions.HTTPError as e:
            def show_error():
                if e.response.status_code == 401:
                    node.status = "Error: Invalid API key"
                elif e.response.status_code == 404:
                    node.status = "Error: Workflow not found"
                elif e.response.status_code == 429:
                    node.status = "Error: Rate limit exceeded"
                else:
                    node.status = f"HTTP Error: {e.response.status_code}"
            
            bpy.app.timers.register(show_error, first_interval=0.1)
            
        except Exception as e:
            def show_error():
                node.status = f"Execution error: {str(e)[:50]}"
            
            bpy.app.timers.register(show_error, first_interval=0.1)
    
    def collect_webhook_data(self, node):
        """Collect data for webhook mode"""
        # Look for webhook data input
        webhook_data = {}
        
        for input_socket in node.inputs[1:]:  # Skip workflow ID
            if input_socket.is_linked:
                socket_data = utils.extract_socket_value(input_socket)
                if socket_data:
                    try:
                        # Try to parse as JSON if it's a string
                        if isinstance(socket_data, str):
                            webhook_data = json.loads(socket_data)
                        else:
                            webhook_data = socket_data
                        break
                    except json.JSONDecodeError:
                        webhook_data[input_socket.name] = socket_data
        
        return webhook_data
    
    def collect_schema_inputs(self, node):
        """Collect structured inputs using paramId_nodeId format"""
        inputs = {}
        
        # Load cached schema to get parameter IDs
        try:
            schema = json.loads(node.schema_data) if node.schema_data else {}
        except:
            schema = {}
        
        for input_socket in node.inputs[1:]:  # Skip workflow ID
            if input_socket.is_linked:
                socket_data = utils.extract_socket_value(input_socket)
                if socket_data is not None:
                    # Get the parameter ID from socket properties
                    param_id = input_socket.get('param_id', input_socket.name)
                    
                    # Format data appropriately for RunChat
                    if input_socket.bl_idname == 'RunChatImageSocket':
                        formatted_data = utils.format_data_for_runchat(socket_data, 'image')
                    elif input_socket.bl_idname == 'RunChatModelSocket':
                        formatted_data = utils.format_data_for_runchat(socket_data, 'model')
                    elif input_socket.bl_idname == 'RunChatWebhookSocket':
                        formatted_data = socket_data
                    else:
                        formatted_data = socket_data
                    
                    inputs[param_id] = formatted_data
        
        # Prepare request with proper structure
        request_data = {
            'inputs': inputs
        }
        
        # Add instance ID if we have one
        if node.instance_id:
            request_data['runchat_instance_id'] = node.instance_id
        
        return request_data
    
    def update_node_results(self, node, result, execution_time):
        try:
            node.execution_time = execution_time
            
            if 'runchat_instance_id' in result:
                node.instance_id = result['runchat_instance_id']
            
            # Process output data
            if 'data' in result:
                for output_data in result['data']:
                    output_id = output_data.get('id', '')
                    output_value = utils.process_runchat_output(output_data.get('data', {}))
                    
                    # Find matching output socket and set data
                    for output_socket in node.outputs:
                        socket_param_id = output_socket.get('param_id', output_socket.name)
                        if socket_param_id == output_id or output_socket.name == output_id:
                            # Store processed data in the node for connected sockets to access
                            setattr(node, f"output_{output_id}", output_value)
                            break
            
            node.status = f"Completed in {execution_time:.2f}s"
            
            # Process metadata if available
            if 'metadata' in result:
                try:
                    metadata = json.loads(result['metadata'])
                    if 'statusMessage' in metadata:
                        node.status += f" - {metadata['statusMessage']}"
                except:
                    pass
            
        except Exception as e:
            node.status = f"Result error: {str(e)}"

# Additional utility operators
class RUNCHAT_OT_CopyId(bpy.types.Operator):
    """Copy workflow ID to clipboard"""
    bl_idname = "runchat.copy_id"
    bl_label = "Copy ID"
    
    workflow_id: StringProperty()
    
    def execute(self, context):
        bpy.context.window_manager.clipboard = self.workflow_id
        self.report({'INFO'}, f"Copied ID: {self.workflow_id}")
        return {'FINISHED'}

class RUNCHAT_OT_ValidateJson(bpy.types.Operator):
    """Validate JSON data"""
    bl_idname = "runchat.validate_json"
    bl_label = "Validate JSON"
    
    node_name: StringProperty()
    
    def execute(self, context):
        node = context.scene.node_tree.nodes.get(self.node_name)
        if not node:
            return {'CANCELLED'}
        
        try:
            json.loads(node.webhook_data)
            self.report({'INFO'}, "JSON is valid")
        except json.JSONDecodeError as e:
            self.report({'ERROR'}, f"Invalid JSON: {str(e)}")
        
        return {'FINISHED'}

class RUNCHAT_OT_FormatJson(bpy.types.Operator):
    """Format JSON data"""
    bl_idname = "runchat.format_json"
    bl_label = "Format JSON"
    
    node_name: StringProperty()
    
    def execute(self, context):
        node = context.scene.node_tree.nodes.get(self.node_name)
        if not node:
            return {'CANCELLED'}
        
        try:
            data = json.loads(node.webhook_data)
            node.webhook_data = json.dumps(data, indent=2)
            self.report({'INFO'}, "JSON formatted")
        except json.JSONDecodeError as e:
            self.report({'ERROR'}, f"Invalid JSON: {str(e)}")
        
        return {'FINISHED'}

class RUNCHAT_OT_OpenEditor(bpy.types.Operator):
    """Open RunChat editor"""
    bl_idname = "runchat.open_editor"
    bl_label = "Open Editor"
    
    workflow_id: StringProperty()
    
    def execute(self, context):
        import webbrowser
        webbrowser.open(f"https://runchat.app/editor?id={self.workflow_id}")
        return {'FINISHED'}

class RUNCHAT_OT_ClearInstance(bpy.types.Operator):
    """Clear RunChat instance"""
    bl_idname = "runchat.clear_instance"
    bl_label = "Clear Instance"
    
    node_name: StringProperty()
    
    def execute(self, context):
        node = context.scene.node_tree.nodes.get(self.node_name)
        if node:
            node.instance_id = ""
            node.status = "Instance cleared - ready for new execution"
        return {'FINISHED'}

class RUNCHAT_OT_SendImage(bpy.types.Operator):
    """Send image through RunChat"""
    bl_idname = "runchat.send_image"
    bl_label = "Send Image"
    
    node_name: StringProperty()
    
    def execute(self, context):
        node = context.scene.node_tree.nodes.get(self.node_name)
        if not node:
            return {'CANCELLED'}
        
        try:
            base64_data = None
            
            # Priority: render result > active image > file path
            if node.use_render_result:
                base64_data = utils.get_active_render_image()
                if not base64_data:
                    self.report({'ERROR'}, "No render result available. Render the scene first.")
                    return {'CANCELLED'}
                    
            elif node.use_active_image:
                # Get active image from UV/Image editor
                for area in context.screen.areas:
                    if area.type == 'IMAGE_EDITOR':
                        if area.spaces.active.image:
                            base64_data = utils.blender_image_to_base64(area.spaces.active.image.name)
                            break
                
                if not base64_data:
                    self.report({'ERROR'}, "No active image found in Image Editor")
                    return {'CANCELLED'}
                    
            else:
                # Get image path from node or connected input
                image_path = None
                
                if node.inputs[0].is_linked:
                    linked_node = node.inputs[0].links[0].from_node
                    if hasattr(linked_node, 'image_path'):
                        image_path = linked_node.image_path
                else:
                    image_path = node.image_path
                
                if not image_path:
                    self.report({'ERROR'}, "No image path specified")
                    return {'CANCELLED'}
                
                # Convert image to base64 with compression
                base64_data = utils.image_to_base64(image_path, node.compression_quality)
            
            if base64_data:
                # Store the base64 data in the node for output
                node.image_data = base64_data
                size_kb = len(base64_data) * 3 / 4 / 1024  # Approximate size in KB
                self.report({'INFO'}, f"Image processed: ~{size_kb:.1f} KB")
            else:
                self.report({'ERROR'}, "Failed to process image")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Image processing error: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class RUNCHAT_OT_ReceiveImage(bpy.types.Operator):
    """Receive image from RunChat"""
    bl_idname = "runchat.receive_image"
    bl_label = "Receive Image"
    
    node_name: StringProperty()
    
    def execute(self, context):
        node = context.scene.node_tree.nodes.get(self.node_name)
        if not node:
            return {'CANCELLED'}
        
        try:
            # Get image data from connected input
            if not node.inputs[0].is_linked:
                self.report({'ERROR'}, "No image data connected")
                return {'CANCELLED'}
            
            linked_node = node.inputs[0].links[0].from_node
            image_data = getattr(linked_node, 'image_data', None)
            
            if not image_data:
                self.report({'ERROR'}, "No image data available")
                return {'CANCELLED'}
            
            saved_path = None
            blender_image = None
            material = None
            
            # Save image to file if auto_save is enabled
            if node.auto_save:
                output_path = bpy.path.abspath(node.save_path)
                saved_path = utils.base64_to_image(image_data, output_path)
                
                if saved_path:
                    node.output_file_path = saved_path
                    self.report({'INFO'}, f"Image saved to: {saved_path}")
                else:
                    self.report({'WARNING'}, "Failed to save image to file")
            
            # Load into Blender if requested
            if node.load_to_blender:
                blender_image = utils.load_image_from_base64(image_data, f"RunChat_Received_{node.name}")
                if blender_image:
                    self.report({'INFO'}, f"Image loaded as: {blender_image.name}")
            
            # Create material if requested
            if node.create_material and blender_image:
                material = bpy.data.materials.new(f"RunChat_Material_{node.name}")
                material.use_nodes = True
                
                # Clear default nodes
                material.node_tree.nodes.clear()
                
                # Add shader nodes
                bsdf = material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
                output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
                tex_image = material.node_tree.nodes.new('ShaderNodeTexImage')
                
                # Set image
                tex_image.image = blender_image
                
                # Connect nodes
                material.node_tree.links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
                material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
                
                # Store material reference
                node.output_material = material
                self.report({'INFO'}, f"Material created: {material.name}")
                
        except Exception as e:
            self.report({'ERROR'}, f"Image receive error: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class RUNCHAT_OT_LoadModel(bpy.types.Operator):
    """Load 3D model from URL"""
    bl_idname = "runchat.load_model"
    bl_label = "Load Model"
    
    node_name: StringProperty()
    
    def execute(self, context):
        node = context.scene.node_tree.nodes.get(self.node_name)
        if not node:
            return {'CANCELLED'}
        
        # Get URL from input or node property
        model_url = None
        if node.inputs[0].is_linked:
            linked_node = node.inputs[0].links[0].from_node
            if hasattr(linked_node, 'model_url'):
                model_url = linked_node.model_url
        else:
            model_url = node.model_url
        
        if not model_url:
            self.report({'ERROR'}, "No model URL specified")
            return {'CANCELLED'}
        
        # Start async model loading
        threading.Thread(target=self.load_model_async, args=(node, model_url)).start()
        node.status = "Loading model..."
        
        return {'FINISHED'}
    
    def load_model_async(self, node, model_url):
        try:
            # Download model file
            response = requests.get(model_url, timeout=120)
            response.raise_for_status()
            
            # Determine file extension
            url_lower = model_url.lower()
            if node.import_format == 'AUTO':
                if '.obj' in url_lower:
                    ext = '.obj'
                elif '.fbx' in url_lower:
                    ext = '.fbx'
                elif '.ply' in url_lower:
                    ext = '.ply'
                elif '.stl' in url_lower:
                    ext = '.stl'
                elif '.gltf' in url_lower or '.glb' in url_lower:
                    ext = '.gltf'
                elif '.blend' in url_lower:
                    ext = '.blend'
                else:
                    ext = '.obj'  # Default
            else:
                ext = f".{node.import_format.lower()}"
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                tmp_file.write(response.content)
                temp_path = tmp_file.name
            
            # Import on main thread
            def import_model():
                self.import_model_file(node, temp_path, ext)
                os.unlink(temp_path)  # Clean up temp file
            
            bpy.app.timers.register(import_model, first_interval=0.1)
            
        except Exception as e:
            def show_error():
                node.status = f"Model load error: {str(e)[:50]}"
            
            bpy.app.timers.register(show_error, first_interval=0.1)
    
    def import_model_file(self, node, filepath, ext):
        try:
            # Clear scene if requested
            if node.clear_scene:
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.delete(use_global=False)
            
            # Store objects before import
            objects_before = set(bpy.context.scene.objects)
            
            # Import based on format
            if ext == '.obj':
                bpy.ops.import_scene.obj(filepath=filepath)
            elif ext == '.fbx':
                bpy.ops.import_scene.fbx(filepath=filepath)
            elif ext == '.ply':
                bpy.ops.import_mesh.ply(filepath=filepath)
            elif ext == '.stl':
                bpy.ops.import_mesh.stl(filepath=filepath)
            elif ext == '.gltf':
                bpy.ops.import_scene.gltf(filepath=filepath)
            elif ext == '.blend':
                # For blend files, append objects
                with bpy.data.libraries.load(filepath) as (data_from, data_to):
                    data_to.objects = data_from.objects
                
                for obj in data_to.objects:
                    bpy.context.scene.collection.objects.link(obj)
            
            # Find newly imported objects
            objects_after = set(bpy.context.scene.objects)
            new_objects = objects_after - objects_before
            
            # Apply scale if specified
            if node.import_scale != 1.0:
                for obj in new_objects:
                    obj.scale = (node.import_scale, node.import_scale, node.import_scale)
            
            # Store model data in node
            node.model_data = {
                'imported_objects': [obj.name for obj in new_objects],
                'file_format': ext,
                'source_url': node.model_url
            }
            
            node.status = f"Model imported: {len(new_objects)} objects"
            
        except Exception as e:
            node.status = f"Import failed: {str(e)[:50]}"

# Node categories for the Add menu
class RunChatNodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'RunChatNodeTree'

node_categories = [
    RunChatNodeCategory("RUNCHAT_CORE", "RunChat Core", items=[
        nodeitems_utils.NodeItem("RunChatExecutorNode"),
        nodeitems_utils.NodeItem("RunChatWebhookNode"),
    ]),
    RunChatNodeCategory("RUNCHAT_IO", "RunChat I/O", items=[
        nodeitems_utils.NodeItem("RunChatImageSendNode"),
        nodeitems_utils.NodeItem("RunChatImageReceiveNode"),
        nodeitems_utils.NodeItem("RunChatModelLoaderNode"),
    ]),
]

# Enhanced registration with all new classes
classes = [
    RunChatNodeTree,
    RunChatImageSocket,
    RunChatModelSocket,
    RunChatDataSocket,
    RunChatWebhookSocket,
    RunChatExecutorNode,
    RunChatImageSendNode,
    RunChatImageReceiveNode,
    RunChatModelLoaderNode,
    RunChatWebhookNode,
    RUNCHAT_OT_LoadSchema,
    RUNCHAT_OT_ReloadSchema,
    RUNCHAT_OT_Execute,
    RUNCHAT_OT_OpenEditor,
    RUNCHAT_OT_ClearInstance,
    RUNCHAT_OT_SendImage,
    RUNCHAT_OT_ReceiveImage,
    RUNCHAT_OT_LoadModel,
    RUNCHAT_OT_CopyId,
    RUNCHAT_OT_ValidateJson,
    RUNCHAT_OT_FormatJson,
    RUNCHAT_OT_CancelLoading,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    nodeitems_utils.register_node_categories("RUNCHAT_NODES", node_categories)

def unregister():
    nodeitems_utils.unregister_node_categories("RUNCHAT_NODES")
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls) 