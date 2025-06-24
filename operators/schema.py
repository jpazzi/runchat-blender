# operators/schema.py

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from .. import api
from .. import preferences


class RUNCHAT_OT_load_schema(Operator):
    """Load RunChat workflow schema"""
    bl_idname = "runchat.load_schema"
    bl_label = "Load Schema"
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if not runchat_props.runchat_id:
            self.report({'ERROR'}, "Please enter a RunChat ID")
            return {'CANCELLED'}
        
        api_key = preferences.get_api_key()
        if not api_key:
            self.report({'ERROR'}, "Please set your RunChat API key in addon preferences")
            return {'CANCELLED'}
        
        print(f"=== SCHEMA LOADING DEBUG ===")
        print(f"Starting schema load for ID: {runchat_props.runchat_id}")
        print(f"API Key present: {'Yes' if api_key else 'No'}")
        print(f"API Key length: {len(api_key) if api_key else 0}")
        
        # Reset state
        runchat_props.schema_loaded = False
        runchat_props.status = "Loading schema..."
        
        # Clear existing inputs/outputs and instance ID (fresh start for new workflow)
        runchat_props.inputs.clear()
        runchat_props.outputs.clear()
        runchat_props.instance_id = ""  # Clear instance ID for new workflow
        
        # Load schema synchronously
        try:
            print(f"Making API call to: {api.RunChatAPI.BASE_URL}/{runchat_props.runchat_id}/schema")
            runchat_props.status = "Contacting RunChat API..."
            
            raw_schema = api.RunChatAPI.get_schema(runchat_props.runchat_id, api_key)
            print(f"API call completed. Response type: {type(raw_schema)}")
            
            if raw_schema:
                print(f"Raw schema keys: {raw_schema.keys() if isinstance(raw_schema, dict) else 'Not a dict'}")
                if isinstance(raw_schema, dict):
                    print(f"Raw schema structure:")
                    for key, value in raw_schema.items():
                        print(f"  {key}: {type(value)} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                        if key in ['inputs', 'outputs'] and isinstance(value, list) and len(value) > 0:
                            print(f"    First item: {value[0]}")
                
                runchat_props.status = "Parsing schema..."
                
                # Parse the schema into a consistent format
                try:
                    schema = self.parse_schema_format(raw_schema)
                    print(f"Schema parsed successfully:")
                    print(f"  Name: {schema.get('name', 'Unknown')}")
                    print(f"  Inputs: {len(schema.get('inputs', []))}")
                    print(f"  Outputs: {len(schema.get('outputs', []))}")
                    
                    if schema.get('inputs'):
                        print(f"  First input: {schema['inputs'][0]}")
                    if schema.get('outputs'):
                        print(f"  First output: {schema['outputs'][0]}")
                    
                    # Update UI directly (synchronous)
                    self.update_ui_direct(runchat_props, schema, None)
                    
                    print(f"UI updated. Schema loaded: {runchat_props.schema_loaded}")
                    print(f"Workflow name: {runchat_props.workflow_name}")
                    print(f"Inputs count: {len(runchat_props.inputs)}")
                    print(f"Outputs count: {len(runchat_props.outputs)}")
                    
                    # Debug: print input details
                    for i, inp in enumerate(runchat_props.inputs):
                        print(f"Input {i}: {inp.name} ({inp.data_type}, UI: {inp.ui_type}) - Required: {inp.required}")
                    
                    self.report({'INFO'}, f"Schema loaded: {len(runchat_props.inputs)} inputs, {len(runchat_props.outputs)} outputs")
                    
                except Exception as e:
                    print(f"Error parsing schema: {e}")
                    print(f"Raw schema: {raw_schema}")
                    error_message = f"Schema parsing error: {str(e)}"
                    runchat_props.status = error_message
                    self.report({'ERROR'}, error_message)
                    return {'CANCELLED'}
            else:
                print("No schema data received from API")
                error_message = "No schema data received from API"
                runchat_props.status = error_message
                self.report({'ERROR'}, error_message)
                return {'CANCELLED'}
                
        except Exception as e:
            print(f"Error in schema loading: {e}")
            import traceback
            print(traceback.format_exc())
            error_message = f"API error: {str(e)}"
            runchat_props.status = error_message
            self.report({'ERROR'}, error_message)
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def parse_schema_format(self, schema):
        """Parse schema from RunChat API BasicParameter format"""
        inputs = []
        outputs = []
        workflow_name = schema.get('name', 'Unknown Workflow')
        
        print(f"Parsing schema: {schema}")
        
        # Handle the actual API format with BasicParameter arrays
        if 'inputs' in schema and isinstance(schema['inputs'], list):
            for item in schema['inputs']:
                # Parse BasicParameter format: {id, label, type?, description?, data}
                if isinstance(item, dict):
                    # Split ID to get param_id and node_id (format: paramId_nodeId)
                    full_id = item.get('id', '')
                    id_parts = full_id.split('_')
                    param_id = id_parts[0] if len(id_parts) > 0 else full_id
                    node_id = id_parts[1] if len(id_parts) > 1 else 'unknown'
                    
                    input_item = {
                        'id': full_id,  # Keep the full ID for execution
                        'paramId': param_id,
                        'nodeId': node_id,
                        'name': item.get('label', param_id),
                        'label': item.get('label', param_id),
                        'description': item.get('description', ''),
                        'dataType': item.get('type', 'string'),
                        'type': item.get('type', 'string'),
                        'data': item.get('data', None),
                        'uiType': 'text',  # Default UI type
                        'required': False  # Default to not required
                    }
                    
                    # Determine UI type based on data type
                    data_type = input_item['dataType'].lower()
                    if data_type in ['image', 'screenshot', 'file']:
                        input_item['uiType'] = 'image'
                    elif 'url' in input_item['name'].lower():
                        input_item['uiType'] = 'url'
                        input_item['isUrlInput'] = True
                    
                    inputs.append(input_item)
                    print(f"Parsed input: {input_item['name']} (type: {input_item['dataType']}, ui: {input_item['uiType']})")
        
        if 'outputs' in schema and isinstance(schema['outputs'], list):
            for item in schema['outputs']:
                # Parse BasicParameter format for outputs
                if isinstance(item, dict):
                    full_id = item.get('id', '')
                    id_parts = full_id.split('_')
                    param_id = id_parts[0] if len(id_parts) > 0 else full_id
                    node_id = id_parts[1] if len(id_parts) > 1 else 'unknown'
                    
                    output_item = {
                        'id': full_id,
                        'paramId': param_id,
                        'nodeId': node_id,
                        'name': item.get('label', param_id),
                        'label': item.get('label', param_id),
                        'dataType': item.get('type', 'string'),
                        'type': item.get('type', 'string'),
                        'data': item.get('data', None)
                    }
                    
                    outputs.append(output_item)
                    print(f"Parsed output: {output_item['name']} (type: {output_item['dataType']})")
        
        return {
            'name': workflow_name,
            'inputs': inputs,
            'outputs': outputs
        }
    
    def update_ui_direct(self, runchat_props, schema, error_message):
        """Direct UI update for synchronous loading"""
        try:
            if schema:
                runchat_props.schema_loaded = True
                runchat_props.workflow_name = schema.get('name', 'Unknown')
                runchat_props.status = f"Schema loaded: {schema.get('name', 'Unknown')}"
                
                # Populate inputs
                for input_data in schema.get('inputs', []):
                    input_prop = runchat_props.inputs.add()
                    input_prop.param_id = input_data.get('id', '')
                    input_prop.node_id = input_data.get('nodeId', '')
                    input_prop.name = input_data.get('name', input_data.get('label', 'Unknown'))
                    input_prop.description = input_data.get('description', '')
                    input_prop.data_type = input_data.get('dataType', input_data.get('type', 'string'))
                    input_prop.ui_type = input_data.get('uiType', 'text')
                    input_prop.required = input_data.get('required', False)
                
                # Populate outputs
                for output_data in schema.get('outputs', []):
                    output_prop = runchat_props.outputs.add()
                    output_prop.param_id = output_data.get('id', '')
                    output_prop.node_id = output_data.get('nodeId', '')
                    output_prop.name = output_data.get('name', output_data.get('label', 'Unknown'))
                    output_prop.data_type = output_data.get('dataType', output_data.get('type', 'string'))
                    
                    data_type = output_prop.data_type.lower()
                    if data_type in ['image', 'screenshot']:
                        output_prop.output_type = 'image'
                    elif data_type in ['gltf', 'model', '3d']:
                        output_prop.output_type = 'gltf'
                    else:
                        output_prop.output_type = 'text'
                
                print(f"Schema loaded: {len(runchat_props.inputs)} inputs, {len(runchat_props.outputs)} outputs")
            else:
                if error_message:
                    runchat_props.status = f"Schema load failed: {error_message}"
                else:
                    runchat_props.status = "Failed to load schema"
        except Exception as e:
            runchat_props.status = f"Error updating UI: {str(e)}"
            print(f"Error in update_ui_direct: {e}")


class RUNCHAT_OT_test_connection(Operator):
    """Test connection to RunChat API"""
    bl_idname = "runchat.test_connection"
    bl_label = "Test Connection"
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        # Check API key
        api_key = preferences.get_api_key()
        if not api_key:
            self.report({'ERROR'}, "Please set your RunChat API key in addon preferences")
            return {'CANCELLED'}
        
        # Check RunChat ID
        if not runchat_props.runchat_id:
            self.report({'ERROR'}, "Please enter a RunChat ID")
            return {'CANCELLED'}
        
        # Test the connection with enhanced debugging
        try:
            runchat_props.status = "Testing connection..."
            
            # First, test if requests module is available
            try:
                import requests
                print("✅ Requests module loaded successfully")
            except ImportError as e:
                runchat_props.status = "Missing requests module"
                self.report({'ERROR'}, "Python requests module not available in Blender")
                print(f"❌ Import error: {e}")
                return {'CANCELLED'}
            
            # Test basic internet connectivity first
            print("🔍 Testing basic connectivity...")
            try:
                # Try a simple HTTP request to a reliable server
                test_response = requests.get("https://httpbin.org/get", timeout=5)
                print(f"✅ Basic internet connectivity: OK (status: {test_response.status_code})")
            except Exception as e:
                print(f"❌ Basic connectivity test failed: {e}")
                runchat_props.status = f"Network connectivity issue: {str(e)}"
                self.report({'ERROR'}, "Network connectivity issue - check your internet connection")
                return {'CANCELLED'}
            
            # Now test RunChat API
            url = f"{api.RunChatAPI.BASE_URL}/{runchat_props.runchat_id}/schema"
            headers = api.RunChatAPI.get_headers(api_key)
            
            print(f"🌐 Testing RunChat API connection...")
            print(f"   URL: {url}")
            print(f"   Headers: {headers}")
            
            # Configure requests session with better settings for Blender
            session = requests.Session()
            session.headers.update(headers)
            
            # Add SSL and proxy handling
            import ssl
            session.verify = True  # Verify SSL certificates
            
            response = session.get(url, timeout=15)
            
            print(f"📡 Response received:")
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Content preview: {response.text[:200]}...")
            
            if response.status_code == 200:
                runchat_props.status = "Connection successful!"
                self.report({'INFO'}, "✅ Connection test successful!")
                print("🎉 RunChat API connection successful!")
            elif response.status_code == 401:
                runchat_props.status = "Authentication failed - check API key"
                self.report({'ERROR'}, "❌ Authentication failed - check your API key")
                print("🔑 Authentication failed - API key issue")
            elif response.status_code == 404:
                runchat_props.status = "RunChat ID not found"
                self.report({'ERROR'}, "❌ RunChat ID not found")
                print("🔍 RunChat ID not found")
            elif response.status_code == 403:
                runchat_props.status = "Access forbidden - check permissions"
                self.report({'ERROR'}, "❌ Access forbidden - check API key permissions")
                print("🚫 Access forbidden")
            else:
                runchat_props.status = f"HTTP {response.status_code}: {response.reason}"
                self.report({'ERROR'}, f"❌ Connection failed: HTTP {response.status_code}")
                print(f"⚠️ Unexpected HTTP status: {response.status_code}")
                
        except requests.exceptions.SSLError as e:
            print(f"🔐 SSL Error: {e}")
            runchat_props.status = "SSL certificate error"
            self.report({'ERROR'}, "SSL certificate error - try updating certificates")
            
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
            runchat_props.status = "Connection timed out"
            self.report({'ERROR'}, "Connection timed out - server may be slow")
            
        except requests.exceptions.ConnectionError as e:
            print(f"🌐 Connection Error: {e}")
            # More specific error handling
            if "Name or service not known" in str(e):
                runchat_props.status = "DNS resolution failed"
                self.report({'ERROR'}, "DNS resolution failed - check internet/DNS settings")
            elif "Connection refused" in str(e):
                runchat_props.status = "Connection refused by server"
                self.report({'ERROR'}, "Connection refused - server may be down")
            elif "No route to host" in str(e):
                runchat_props.status = "Network routing issue"
                self.report({'ERROR'}, "Network routing issue - check firewall/proxy")
            else:
                runchat_props.status = "Network connection error"
                self.report({'ERROR'}, "Network connection error - check internet connection")
            
        except requests.exceptions.ProxyError as e:
            print(f"🔀 Proxy Error: {e}")
            runchat_props.status = "Proxy configuration error"
            self.report({'ERROR'}, "Proxy error - check proxy settings")
            
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            
            runchat_props.status = f"Unexpected error: {str(e)}"
            self.report({'ERROR'}, f"Unexpected error: {str(e)}")
        
        return {'FINISHED'}


class RUNCHAT_OT_load_examples(Operator):
    """Load workflow examples for Blender"""
    bl_idname = "runchat.load_examples"
    bl_label = "Load Examples"
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        print("=== LOADING BLENDER EXAMPLES ===")
        
        # Check if requests module is available
        try:
            import requests
            print("✅ Requests module available")
        except ImportError as e:
            print(f"❌ Requests module not available: {e}")
            runchat_props.examples_loaded = False
            runchat_props.examples_loading = False
            self.report({'ERROR'}, "Python requests module not available in Blender")
            return {'CANCELLED'}
        
        # Set loading state
        runchat_props.examples_loading = True
        
        # Clear existing examples
        runchat_props.examples.clear()
        
        try:
            print("Calling API to fetch examples...")
            # Fetch examples from API - simple approach
            examples_data = api.RunChatAPI.get_examples_for_plugin("blender")
            
            print(f"API returned: {examples_data}")
            print(f"API data type: {type(examples_data)}")
            
            if examples_data and isinstance(examples_data, dict) and 'examples' in examples_data:
                examples = examples_data['examples']
                print(f"Loading {len(examples)} examples...")
                
                # Simple processing
                for i, example_data in enumerate(examples):
                    print(f"Processing example {i}: {example_data}")
                    example_prop = runchat_props.examples.add()
                    example_prop.example_id = example_data.get('id', '')
                    example_prop.name = example_data.get('name', 'Unknown Example')
                    print(f"Added: '{example_prop.name}' (ID: '{example_prop.example_id}')")
                
                runchat_props.examples_loaded = True
                runchat_props.examples_loading = False
                self.report({'INFO'}, f"Loaded {len(examples)} examples")
                print(f"✅ Loaded {len(examples)} examples")
                
            elif examples_data is None:
                print("API returned None - likely a network or server error")
                runchat_props.examples_loaded = False
                runchat_props.examples_loading = False
                self.report({'ERROR'}, "Failed to connect to examples API - check your internet connection")
                
            else:
                print(f"Unexpected API response format: {examples_data}")
                runchat_props.examples_loaded = False
                runchat_props.examples_loading = False
                self.report({'ERROR'}, "Unexpected response format from examples API")
                
        except Exception as e:
            print(f"Exception in load_examples: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            runchat_props.examples_loaded = False
            runchat_props.examples_loading = False
            self.report({'ERROR'}, f"Failed to load examples: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class RUNCHAT_OT_use_example(Operator):
    """Use a workflow example by loading its schema"""
    bl_idname = "runchat.use_example"
    bl_label = "Use Example"
    
    example_id: StringProperty()
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if not self.example_id:
            self.report({'ERROR'}, "No example ID provided")
            return {'CANCELLED'}
        
        print(f"Using example with ID: {self.example_id}")
        
        # Set the runchat_id and load schema
        runchat_props.runchat_id = self.example_id
        
        # Trigger schema loading
        bpy.ops.runchat.load_schema()
        
        return {'FINISHED'}


classes = [
    RUNCHAT_OT_load_schema,
    RUNCHAT_OT_test_connection,
    RUNCHAT_OT_load_examples,
    RUNCHAT_OT_use_example,
] 