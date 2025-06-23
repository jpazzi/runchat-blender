# operators/execution.py

import bpy
import threading
from bpy.types import Operator
from bpy.props import IntProperty

from .. import api
from .. import preferences


def log_to_blender(message, level='INFO', operator=None):
    """Log message to Blender's Info log"""
    print(f"[RunChat] {message}")
    # If we have an operator reference, use self.report to show in Info log
    if operator and hasattr(operator, 'report'):
        try:
            report_type = 'ERROR' if level == 'ERROR' else 'INFO'
            operator.report({report_type}, f"RunChat: {message}")
        except:
            pass


class RUNCHAT_OT_execute(Operator):
    """Execute RunChat workflow"""
    bl_idname = "runchat.execute"
    bl_label = "Execute RunChat"
    
    def execute(self, context):
        scene = context.scene
        runchat_props = scene.runchat_properties
        
        if not runchat_props.schema_loaded:
            self.report({'ERROR'}, "Please load schema first")
            log_to_blender("Execution failed: Schema not loaded", 'ERROR')
            return {'CANCELLED'}
        
        api_key = preferences.get_api_key()
        if not api_key:
            self.report({'ERROR'}, "Please set your RunChat API key in addon preferences")
            log_to_blender("Execution failed: No API key set", 'ERROR')
            return {'CANCELLED'}
        
        # Prepare inputs
        inputs = {}
        missing_required = []
        
        for input_prop in runchat_props.inputs:
            key = input_prop.param_id  # Use the full ID (paramId_nodeId) directly
            
            # Determine what value to use for this input
            value = None
            
            # For ALL text inputs, prioritize uploaded URL if available, then text input
            if input_prop.uploaded_url:
                # Use uploaded URL if available (this takes precedence)
                value = input_prop.uploaded_url
            elif input_prop.text_value:
                # Use manual text input if no uploaded URL
                value = input_prop.text_value
            elif input_prop.required:
                # Missing required input
                missing_required.append(input_prop.name)
            
            if value:
                inputs[key] = value
        
        # Check for missing required inputs
        if missing_required:
            error_msg = f"Missing required inputs: {', '.join(missing_required)}"
            self.report({'ERROR'}, error_msg)
            log_to_blender(f"Execution failed: {error_msg}", 'ERROR')
            return {'CANCELLED'}
        
        log_to_blender("=== EXECUTION DEBUG INFO ===")
        log_to_blender(f"RunChat ID: {runchat_props.runchat_id}")
        log_to_blender(f"API Key present: {'Yes' if api_key else 'No'}")
        log_to_blender(f"API Key length: {len(api_key) if api_key else 0}")
        log_to_blender(f"Inputs prepared: {inputs}")
        log_to_blender(f"Number of inputs: {len(inputs)}")
        log_to_blender(f"Instance ID: {runchat_props.instance_id}")
        
        # Set initial status and start progress monitoring
        runchat_props.status = "Starting execution..."
        runchat_props.progress = 0.0
        runchat_props.progress_message = "Initializing..."
        
        # Clear previous output values to show running status
        for output_prop in runchat_props.outputs:
            output_prop.value = ""
            output_prop.is_processed = False
            output_prop.output_type = "text"  # Reset to default type
        
        # Execute in background
        thread = threading.Thread(target=self.execute_async, args=(runchat_props, api_key, inputs))
        thread.daemon = True
        thread.start()
        
        # Register a timer to update the UI periodically during execution
        def check_execution_progress():
            # Force UI redraw to show progress updates
            for area in bpy.context.screen.areas:
                if area.type == 'PROPERTIES':
                    area.tag_redraw()
            
            # Continue checking if we're still executing
            if runchat_props.progress < 1.0 and "Executing" in runchat_props.status:
                return 0.5  # Check again in 0.5 seconds
            else:
                return None  # Stop the timer
        
        bpy.app.timers.register(check_execution_progress, first_interval=0.1)
        
        self.report({'INFO'}, "Executing RunChat workflow...")
        log_to_blender("Execution thread started")
        log_to_blender(f"Thread daemon: {thread.daemon}, Thread alive: {thread.is_alive()}")
        return {'FINISHED'}
    
    def execute_async(self, runchat_props, api_key, inputs):
        """Execute workflow - simplified since uploads are handled separately"""
        try:
            log_to_blender("=== ASYNC EXECUTION STARTED ===")
            log_to_blender(f"Thread ID: {threading.current_thread().ident}")
            log_to_blender(f"RunChat ID: {runchat_props.runchat_id}")
            log_to_blender(f"Inputs: {inputs}")
            log_to_blender(f"Instance ID: {runchat_props.instance_id}")
            
            # Set initial status
            def update_initial_status():
                runchat_props.status = "Executing workflow..."
                runchat_props.progress = 0.1
                runchat_props.progress_message = "Sending request to Runchat..."
                for area in bpy.context.screen.areas:
                    if area.type == 'PROPERTIES':
                        area.tag_redraw()
            
            bpy.app.timers.register(update_initial_status, first_interval=0.1)
            
            # Execute workflow
            def update_execution_progress():
                runchat_props.progress = 0.6
                runchat_props.progress_message = "Runchat is processing..."
                for area in bpy.context.screen.areas:
                    if area.type == 'PROPERTIES':
                        area.tag_redraw()
            
            bpy.app.timers.register(update_execution_progress, first_interval=0.5)
            
            log_to_blender("Making API call to RunChat...")
            
            # Execute the workflow
            result = api.RunChatAPI.run_workflow(runchat_props.runchat_id, api_key, inputs, runchat_props.instance_id)
            
            log_to_blender(f"API call completed. Result type: {type(result)}")
            if result:
                log_to_blender(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
                if isinstance(result, dict):
                    log_to_blender(f"Result content: {result}")
            else:
                log_to_blender("No result returned from API")
            
            if result:
                # Update UI with results
                def update_ui():
                    runchat_props.progress = 1.0
                    runchat_props.progress_message = "Complete!"
                    runchat_props.status = "Execution completed successfully"
                    
                    # Process outputs from 'data' array (new API format)
                    if 'data' in result and isinstance(result['data'], list):
                        log_to_blender(f"Processing {len(result['data'])} outputs from data array...")
                        for output_item in result['data']:
                            if isinstance(output_item, dict) and 'id' in output_item:
                                output_id = output_item['id']
                                output_data = output_item.get('data', [])
                                
                                # Handle both single values and arrays
                                if isinstance(output_data, list):
                                    if len(output_data) == 1:
                                        # Single value
                                        output_value = output_data[0]
                                    else:
                                        # Array of values - keep as array for processing
                                        output_value = output_data
                                else:
                                    output_value = output_data
                                
                                log_to_blender(f"Output {output_id}: {output_value}")
                                
                                # Find matching output property
                                for output_prop in runchat_props.outputs:
                                    if output_prop.param_id == output_id:
                                        # Determine output type for better UI
                                        if isinstance(output_value, list):
                                            # Array - check first item for type
                                            first_item = output_value[0] if output_value else ""
                                            if isinstance(first_item, str) and first_item.startswith('http'):
                                                # Check file extensions for different media types
                                                if any(ext in first_item.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff']):
                                                    output_prop.output_type = 'image'
                                                elif any(ext in first_item.lower() for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']):
                                                    output_prop.output_type = 'video'
                                                elif any(ext in first_item.lower() for ext in ['.gltf', '.glb', '.obj', '.fbx', '.dae', '.3ds', '.blend']):
                                                    output_prop.output_type = 'model'
                                                else:
                                                    output_prop.output_type = 'text'
                                            else:
                                                output_prop.output_type = 'text'
                                        elif isinstance(output_value, str):
                                            if output_value.startswith('http'):
                                                # Check file extensions for different media types
                                                if any(ext in output_value.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff']):
                                                    output_prop.output_type = 'image'
                                                elif any(ext in output_value.lower() for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']):
                                                    output_prop.output_type = 'video'
                                                elif any(ext in output_value.lower() for ext in ['.gltf', '.glb', '.obj', '.fbx', '.dae', '.3ds', '.blend']):
                                                    output_prop.output_type = 'model'
                                                else:
                                                    output_prop.output_type = 'text'
                                            else:
                                                output_prop.output_type = 'text'
                                        else:
                                            output_prop.output_type = 'text'
                                        
                                        # Set value as string for UI display
                                        if isinstance(output_value, list):
                                            output_prop.value = str(output_value[0]) if output_value else ""
                                        else:
                                            output_prop.value = str(output_value)
                                        
                                        output_prop.is_processed = True
                                        log_to_blender(f"Updated output {output_id} with type {output_prop.output_type}")
                                        
                                        # Auto-display images immediately (handle arrays)
                                        if output_prop.output_type == 'image':
                                            try:
                                                # Use new array processing function
                                                utils.process_image_array(output_value, output_id, output_prop, runchat_props)
                                            except Exception as e:
                                                log_to_blender(f"Error processing image output: {e}", 'WARNING')
                                        
                                        break
                    # Fallback: try legacy 'outputs' format for backward compatibility
                    elif 'outputs' in result:
                        log_to_blender(f"Processing {len(result['outputs'])} outputs from legacy format...")
                        for output_id, output_value in result['outputs'].items():
                            log_to_blender(f"Output {output_id}: {output_value}")
                            # Find matching output property
                            for output_prop in runchat_props.outputs:
                                if output_prop.param_id == output_id:
                                    output_prop.value = str(output_value)
                                    
                                    # Determine output type for better UI
                                    if isinstance(output_value, str):
                                        if output_value.startswith('http') and any(ext in output_value.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                                            output_prop.output_type = 'image'
                                        elif output_value.startswith('http') and '.gltf' in output_value.lower():
                                            output_prop.output_type = 'gltf'
                                        else:
                                            output_prop.output_type = 'text'
                                    else:
                                        output_prop.output_type = 'text'
                                                                    
                                output_prop.is_processed = True
                                log_to_blender(f"Updated output {output_id} with type {output_prop.output_type}")
                                
                                # Auto-display images immediately
                                if output_prop.output_type == 'image':
                                    try:
                                        # Load and display the image
                                        if output_value.startswith('http'):
                                            image = utils.load_image_from_url(output_value, output_prop.name)
                                        else:
                                            image = utils.load_image_from_base64(output_value, output_prop.name)
                                        
                                        if image:
                                            utils.auto_display_image(image.name)
                                    except Exception as e:
                                        log_to_blender(f"Error auto-displaying image: {e}", 'WARNING')
                                
                                break
                    else:
                        log_to_blender("No outputs found in result (no 'data' or 'outputs' key)")
                    
                    # Update instance ID if provided (check both possible keys)
                    if 'runchat_instance_id' in result:
                        runchat_props.instance_id = result['runchat_instance_id']
                        log_to_blender(f"Updated instance ID: {result['runchat_instance_id']}")
                    elif 'instance_id' in result:
                        runchat_props.instance_id = result['instance_id']
                        log_to_blender(f"Updated instance ID: {result['instance_id']}")
                    
                    log_to_blender(f"Execution completed successfully. Outputs: {result.get('outputs', {})}")
                    
                    # Clear progress after a delay
                    def clear_progress():
                        runchat_props.progress = 0.0
                        runchat_props.progress_message = ""
                        for area in bpy.context.screen.areas:
                            if area.type == 'PROPERTIES':
                                area.tag_redraw()
                    
                    bpy.app.timers.register(clear_progress, first_interval=3.0)
                    
                    # Force UI redraw
                    for area in bpy.context.screen.areas:
                        if area.type == 'PROPERTIES':
                            area.tag_redraw()
                
                bpy.app.timers.register(update_ui, first_interval=0.1)
            else:
                # Handle execution failure
                def update_error():
                    runchat_props.status = "Execution failed - no result returned"
                    runchat_props.progress = 0.0
                    runchat_props.progress_message = ""
                    for area in bpy.context.screen.areas:
                        if area.type == 'PROPERTIES':
                            area.tag_redraw()
                
                bpy.app.timers.register(update_error, first_interval=0.1)
                log_to_blender("Execution failed - no result returned", 'ERROR')
                
        except Exception as e:
            # Handle execution error
            def update_error():
                runchat_props.status = f"Execution error: {str(e)}"
                runchat_props.progress = 0.0
                runchat_props.progress_message = ""
                for area in bpy.context.screen.areas:
                    if area.type == 'PROPERTIES':
                        area.tag_redraw()
            
            bpy.app.timers.register(update_error, first_interval=0.1)
            log_to_blender(f"Execution error in thread: {e}", 'ERROR')
            import traceback
            log_to_blender(f"Full traceback: {traceback.format_exc()}", 'ERROR')
        
        finally:
            log_to_blender("=== ASYNC EXECUTION COMPLETED ===")
            log_to_blender(f"Thread ID: {threading.current_thread().ident}")
            log_to_blender("Thread is finishing")







classes = [
    RUNCHAT_OT_execute,
]