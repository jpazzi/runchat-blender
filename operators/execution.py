# operators/execution.py

import bpy
import threading
import time
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
        
        # Clear credit error state from previous executions
        runchat_props.has_credit_error = False
        runchat_props.credit_error_message = ""
        
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
        """Execute workflow asynchronously in a separate thread"""
        log_to_blender("=== ASYNC EXECUTION STARTED ===")
        log_to_blender(f"Thread ID: {threading.current_thread().ident}")
        log_to_blender(f"Inputs: {inputs}")
        
        try:
            log_to_blender(f"RunChat ID: {runchat_props.runchat_id}")
            log_to_blender(f"Instance ID: {runchat_props.instance_id}")
            
            # Better progress updates
            def update_progress(progress, message):
                runchat_props.progress = progress
                runchat_props.progress_message = message
                log_to_blender(f"Progress: {int(progress*100)}% - {message}")
            
            # Set initial status
            update_progress(0.1, "Initializing...")
            runchat_props.status = "Executing workflow..."
            
            update_progress(0.2, "Sending request to RunChat...")
            log_to_blender("Making API call to RunChat...")
            
            # Start progress simulation timer
            progress_step = 0.2
            max_progress = 0.8
            
            def simulate_progress():
                nonlocal progress_step
                if progress_step < max_progress and "Executing" in runchat_props.status:
                    progress_step += 0.05  # Increment by 5%
                    update_progress(progress_step, f"Workflow executing... ({int(progress_step*100)}%)")
                    return 2.0  # Check again in 2 seconds
                return None  # Stop timer
            
            # Start progress simulation
            bpy.app.timers.register(simulate_progress, first_interval=2.0)
            
            # Execute the workflow (this will block until complete)
            log_to_blender("Starting workflow execution (this may take a while)...")
            
            result = api.RunChatAPI.run_workflow(runchat_props.runchat_id, api_key, inputs, runchat_props.instance_id)
            
            log_to_blender(f"Workflow execution completed. Result type: {type(result)}")
            if result:
                log_to_blender(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
                if isinstance(result, dict):
                    log_to_blender(f"Result content: {result}")
            else:
                log_to_blender("No result returned from API")
            
            # Check for error responses first
            if result and isinstance(result, dict) and result.get('error'):
                log_to_blender("Detected error response from API", 'ERROR')
                error_message = result.get('message', 'Unknown error occurred')
                is_credit_error = result.get('is_credit_error', False)
                status_code = result.get('status_code', 0)
                
                if is_credit_error:
                    log_to_blender(f"Credit error detected: {error_message}", 'ERROR')
                    # Set specific credit error status
                    update_progress(1.0, "Credit limit reached")
                    runchat_props.status = "Credit Error"
                    
                    # Store credit error details for UI display
                    runchat_props.credit_error_message = api.format_credit_error(error_message)
                    runchat_props.has_credit_error = True
                    
                    log_to_blender(f"Credit error stored: {runchat_props.credit_error_message}", 'ERROR')
                else:
                    # Other types of errors
                    update_progress(1.0, "Execution failed")
                    runchat_props.status = f"API Error ({status_code}): {error_message}"
                    runchat_props.has_credit_error = False
                
                return  # Exit early for error cases
            
            elif result:
                # Process results
                log_to_blender("=== PROCESSING RESULTS ===")
                update_progress(0.85, "Processing outputs...")
                runchat_props.status = "Processing outputs..."
                
                # Check for the new 'data' format first (could be array or dict)
                if 'data' in result:
                    data_content = result['data']
                    log_to_blender(f"Found 'data' in result - type: {type(data_content)}")
                    
                    # Handle array format (new API format with output objects)
                    if isinstance(data_content, list):
                        log_to_blender(f"Processing {len(data_content)} outputs from data array...")
                        for i, output_item in enumerate(data_content):
                            if isinstance(output_item, dict) and 'id' in output_item:
                                output_id = output_item['id']
                                output_data = output_item.get('data', [])
                                
                                update_progress(0.85 + (i / len(data_content)) * 0.1, f"Processing output {i+1}/{len(data_content)}")
                                
                                log_to_blender(f"=== PROCESSING ARRAY OUTPUT: {output_id} ===")
                                log_to_blender(f"Output data type: {type(output_data)}")
                                log_to_blender(f"Output data content: {str(output_data)[:200]}...")
                                
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
                                
                                log_to_blender(f"Final output_value: {output_value}")
                                
                                # Find matching output property and process it
                                matching_prop = None
                                for output_prop in runchat_props.outputs:
                                    log_to_blender(f"Checking output prop: {output_prop.param_id} vs {output_id}")
                                    if output_prop.param_id == output_id:
                                        matching_prop = output_prop
                                        break
                                
                                if matching_prop:
                                    log_to_blender(f"Found matching property: {matching_prop.name}")
                                    
                                    # Process the output - use static method to avoid self reference
                                    RUNCHAT_OT_execute.process_output_static(matching_prop, output_value, output_id, runchat_props)
                                else:
                                    log_to_blender(f"No matching output property found for: {output_id}", 'WARNING')
                                    log_to_blender(f"Available output properties: {[prop.param_id for prop in runchat_props.outputs]}")
                    
                    # Handle dict format (direct id->value mapping)
                    elif isinstance(data_content, dict):
                        log_to_blender(f"Found 'data' dict format with {len(data_content)} outputs")
                        log_to_blender(f"Data keys: {list(data_content.keys())}")
                        
                        for i, (output_id, output_value) in enumerate(data_content.items()):
                            update_progress(0.85 + (i / len(data_content)) * 0.1, f"Processing output {i+1}/{len(data_content)}")
                            
                            log_to_blender(f"=== PROCESSING DICT OUTPUT: {output_id} ===")
                            log_to_blender(f"Output value type: {type(output_value)}")
                            log_to_blender(f"Output value content: {str(output_value)[:200]}...")
                            
                            # Find matching output property
                            matching_prop = None
                            for output_prop in runchat_props.outputs:
                                log_to_blender(f"Checking output prop: {output_prop.param_id} vs {output_id}")
                                if output_prop.param_id == output_id:
                                    matching_prop = output_prop
                                    break
                            
                            if matching_prop:
                                log_to_blender(f"Found matching property: {matching_prop.name}")
                                
                                # Process the output - use static method to avoid self reference
                                RUNCHAT_OT_execute.process_output_static(matching_prop, output_value, output_id, runchat_props)
                            else:
                                log_to_blender(f"No matching output property found for: {output_id}", 'WARNING')
                                log_to_blender(f"Available output properties: {[prop.param_id for prop in runchat_props.outputs]}")
                    else:
                        log_to_blender(f"Unknown data format type: {type(data_content)}", 'WARNING')
                
                else:
                    log_to_blender("No outputs found in result (no 'data' or 'outputs' key)")
                    log_to_blender(f"Available result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                    
                # Update instance ID if provided (check both possible keys)
                if 'runchat_instance_id' in result:
                    runchat_props.instance_id = result['runchat_instance_id']
                    log_to_blender(f"Updated instance ID: {result['runchat_instance_id']}")
                elif 'instance_id' in result:
                    runchat_props.instance_id = result['instance_id']
                    log_to_blender(f"Updated instance ID: {result['instance_id']}")
                    
                # Schedule auto-imports after a short delay to avoid blocking
                def schedule_auto_imports():
                    try:
                        update_progress(0.95, "Auto-importing outputs...")
                        log_to_blender("=== STARTING AUTO-IMPORT PROCESS ===")
                        
                        # Count outputs to import
                        import_count = 0
                        for output_prop in runchat_props.outputs:
                            if output_prop.is_processed and output_prop.value and output_prop.value != "No output yet":
                                if output_prop.output_type in ['image', 'video', 'model']:
                                    import_count += 1
                        
                        if import_count > 0:
                            log_to_blender(f"Found {import_count} outputs to auto-import")
                            update_progress(0.95, f"Auto-importing {import_count} outputs...")
                        else:
                            log_to_blender("No outputs found for auto-import")
                            update_progress(0.95, "Finalizing...")
                        
                        # Schedule the auto-imports
                        RUNCHAT_OT_execute.schedule_safe_auto_imports(runchat_props)
                    except Exception as e:
                        log_to_blender(f"Error scheduling auto-imports: {e}", 'WARNING')
                    
                    # Final completion
                    update_progress(1.0, "Complete! Outputs auto-imported.")
                    runchat_props.status = "Ready"
                    
                    # Clear progress after delay
                    def clear_progress():
                        runchat_props.progress = 0.0
                        runchat_props.progress_message = ""
                        return None
                    
                    bpy.app.timers.register(clear_progress, first_interval=2.0)
                    return None
                
                # Schedule the auto-imports with a delay
                bpy.app.timers.register(schedule_auto_imports, first_interval=1.0)
                
            else:
                # No result returned
                update_progress(1.0, "Execution failed")
                runchat_props.status = "Execution failed - no result returned"
                log_to_blender("Execution failed - no result returned", 'ERROR')
                
        except Exception as e:
            log_to_blender(f"Exception in execution thread: {e}", 'ERROR')
            import traceback
            log_to_blender(f"Traceback: {traceback.format_exc()}", 'ERROR')
            
            runchat_props.progress = 0.0
            runchat_props.progress_message = ""
            runchat_props.status = f"Execution failed: {str(e)}"
    
    @staticmethod
    def process_output_static(output_prop, output_value, output_id, runchat_props):
        """Static method to process output without self reference"""
        log_to_blender(f"=== PROCESSING OUTPUT: {output_id} ===")
        log_to_blender(f"Output value type: {type(output_value)}")
        log_to_blender(f"Output value: {str(output_value)[:200]}...")
        
        try:
            # Handle different data formats
            if isinstance(output_value, list):
                log_to_blender(f"Processing array with {len(output_value)} items: {output_value}")
                
                if len(output_value) == 1:
                    # Single URL in array
                    url = output_value[0]
                    log_to_blender(f"Single URL from array: {url}")
                    
                    # Check if URL is valid and not empty
                    if url and str(url).strip():
                        output_prop.value = str(url).strip()
                        
                        # Detect file type from URL
                        if isinstance(url, str) and url.startswith('http'):
                            if any(ext in url.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                                output_prop.output_type = 'image'
                                log_to_blender(f"DETECTED IMAGE OUTPUT! URL: {url}")
                            elif any(ext in url.lower() for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']):
                                output_prop.output_type = 'video'
                                log_to_blender(f"DETECTED VIDEO OUTPUT! URL: {url}")
                            elif any(ext in url.lower() for ext in ['.gltf', '.glb', '.obj', '.fbx', '.dae', '.3ds', '.blend']):
                                output_prop.output_type = 'model'
                                log_to_blender(f"DETECTED MODEL OUTPUT! URL: {url}")
                            else:
                                output_prop.output_type = 'text'
                                log_to_blender(f"URL detected but no recognized file extension: {url}")
                        else:
                            output_prop.output_type = 'text'
                            log_to_blender(f"Non-HTTP URL or not a string: {type(url)} = {url}")
                    else:
                        # Empty or null value in array
                        log_to_blender(f"Empty or null value in single-item array: {repr(url)}")
                        output_prop.value = "Processing..."
                        output_prop.output_type = 'text'
                        
                elif len(output_value) > 1:
                    # Multiple values - check if they're all valid URLs
                    valid_urls = [str(v).strip() for v in output_value if v and str(v).strip()]
                    if valid_urls:
                        output_prop.value = ", ".join(valid_urls)
                        output_prop.output_type = 'text'
                        log_to_blender(f"Multiple valid URLs combined: {output_prop.value}")
                    else:
                        log_to_blender(f"Multiple values but all empty/invalid: {output_value}")
                        output_prop.value = "Processing..."
                        output_prop.output_type = 'text'
                else:
                    # Empty array - this might be temporary while processing
                    log_to_blender(f"Empty array received - output may still be processing")
                    output_prop.value = "Processing..."
                    output_prop.output_type = 'text'
                    
            elif isinstance(output_value, str):
                # Direct string value
                log_to_blender(f"Processing string value: '{output_value}' (length: {len(output_value)})")
                
                # Check if string is valid and not empty
                if output_value and output_value.strip():
                    cleaned_value = output_value.strip()
                    output_prop.value = cleaned_value
                    
                    # Detect file type from URL
                    if cleaned_value.startswith('http'):
                        if any(ext in cleaned_value.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                            output_prop.output_type = 'image'
                            log_to_blender(f"DETECTED IMAGE OUTPUT! URL: {cleaned_value}")
                        elif any(ext in cleaned_value.lower() for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']):
                            output_prop.output_type = 'video'
                            log_to_blender(f"DETECTED VIDEO OUTPUT! URL: {cleaned_value}")
                        elif any(ext in cleaned_value.lower() for ext in ['.gltf', '.glb', '.obj', '.fbx', '.dae', '.3ds', '.blend']):
                            output_prop.output_type = 'model'
                            log_to_blender(f"DETECTED MODEL OUTPUT! URL: {cleaned_value}")
                        else:
                            output_prop.output_type = 'text'
                            log_to_blender(f"HTTP URL but no recognized extension: {cleaned_value}")
                    else:
                        output_prop.output_type = 'text'
                        log_to_blender(f"Non-HTTP string value: {cleaned_value}")
                else:
                    # Empty string
                    log_to_blender(f"Empty or whitespace-only string received")
                    output_prop.value = "Processing..."
                    output_prop.output_type = 'text'
                    
            else:
                # Other data type - convert to string
                log_to_blender(f"Processing other data type: {type(output_value)} = {output_value}")
                if output_value is not None:
                    output_prop.value = str(output_value)
                    output_prop.output_type = 'text'
                else:
                    log_to_blender(f"Received None/null value - output may still be processing")
                    output_prop.value = "Processing..."
                    output_prop.output_type = 'text'
                
            output_prop.is_processed = True
            log_to_blender(f"✅ Updated output {output_id} with type {output_prop.output_type}, value: '{output_prop.value[:100]}...'")
            
            # If output shows "Processing...", schedule a retry check
            if output_prop.value == "Processing...":
                log_to_blender(f"⏳ Output {output_id} is still processing - will check again")
                
                def retry_output_check():
                    try:
                        log_to_blender(f"🔄 Retrying output check for {output_id}")
                        # This is just a placeholder - in practice, the full workflow result should be re-processed
                        # For now, we'll just log that we attempted a retry
                        log_to_blender(f"Retry scheduled for output {output_id} (implement re-processing if needed)")
                    except Exception as e:
                        log_to_blender(f"Error in retry check: {e}", 'WARNING')
                    return None
                
                # Schedule a retry check in 3 seconds
                bpy.app.timers.register(retry_output_check, first_interval=3.0)
            
        except Exception as e:
            log_to_blender(f"Error processing output {output_id}: {e}", 'ERROR')
            output_prop.value = f"Error processing output: {str(e)}"
            output_prop.output_type = 'text'
            output_prop.is_processed = True

    def process_output(self, output_prop, output_value, output_id, runchat_props):
        """Instance method wrapper for static method"""
        RUNCHAT_OT_execute.process_output_static(output_prop, output_value, output_id, runchat_props)
    
    @staticmethod
    def auto_import_outputs(runchat_props):
        """Automatically import outputs to appropriate Blender editors (DEPRECATED - use schedule_safe_auto_imports instead)"""
        log_to_blender("=== AUTO-IMPORTING OUTPUTS (DEPRECATED) ===")
        # This method is deprecated to avoid thread blocking
        pass
    
    @staticmethod
    def schedule_safe_auto_imports(runchat_props):
        """Schedule safe auto-imports for outputs without blocking threads"""
        log_to_blender("=== SCHEDULING SAFE AUTO-IMPORTS ===")
        
        images_scheduled = 0
        videos_scheduled = 0
        models_scheduled = 0
        
        for i, output_prop in enumerate(runchat_props.outputs):
            if (output_prop.is_processed and 
                output_prop.value and 
                output_prop.value not in ["No output yet", "Processing...", ""]):
                log_to_blender(f"Checking output {i}: {output_prop.name} (type: {output_prop.output_type})")
                
                if output_prop.output_type == 'image':
                    # Images are safe to auto-import
                    def import_image_delayed(output_index=i):
                        def do_import():
                            try:
                                log_to_blender(f"Auto-importing image for output {output_index}")
                                bpy.ops.runchat.view_image('EXEC_DEFAULT', output_index=output_index)
                                log_to_blender(f"✅ Auto-imported image for output {output_index}")
                            except Exception as e:
                                log_to_blender(f"Failed to auto-import image {output_index}: {e}", 'WARNING')
                            return None
                        return do_import
                    
                    # Schedule image import with a small delay
                    bpy.app.timers.register(import_image_delayed(), first_interval=0.5 + (i * 0.2))
                    images_scheduled += 1
                
                elif output_prop.output_type == 'video':
                    # Auto-import videos to Video Sequencer
                    def import_video_delayed(output_index=i):
                        def do_import():
                            try:
                                log_to_blender(f"Auto-importing video for output {output_index}")
                                bpy.ops.runchat.import_video('EXEC_DEFAULT', output_index=output_index)
                                log_to_blender(f"✅ Auto-imported video for output {output_index}")
                            except Exception as e:
                                log_to_blender(f"Failed to auto-import video {output_index}: {e}", 'WARNING')
                            return None
                        return do_import
                    
                    # Schedule video import with a longer delay to ensure image imports complete first
                    bpy.app.timers.register(import_video_delayed(), first_interval=1.0 + (i * 0.3))
                    videos_scheduled += 1
                
                elif output_prop.output_type == 'model':
                    # Auto-import 3D models to scene
                    def import_model_delayed(output_index=i):
                        def do_import():
                            try:
                                log_to_blender(f"Auto-importing 3D model for output {output_index}")
                                bpy.ops.runchat.import_model('EXEC_DEFAULT', output_index=output_index)
                                log_to_blender(f"✅ Auto-imported 3D model for output {output_index}")
                            except Exception as e:
                                log_to_blender(f"Failed to auto-import model {output_index}: {e}", 'WARNING')
                            return None
                        return do_import
                    
                    # Schedule model import with the longest delay to ensure other imports complete first
                    bpy.app.timers.register(import_model_delayed(), first_interval=1.5 + (i * 0.3))
                    models_scheduled += 1
        
        # Log summary of scheduled imports
        total_scheduled = images_scheduled + videos_scheduled + models_scheduled
        log_to_blender(f"=== AUTO-IMPORT SUMMARY ===")
        log_to_blender(f"📸 Images scheduled: {images_scheduled}")
        log_to_blender(f"🎬 Videos scheduled: {videos_scheduled}")
        log_to_blender(f"🎭 Models scheduled: {models_scheduled}")
        log_to_blender(f"📋 Total outputs to auto-import: {total_scheduled}")
        
        if total_scheduled > 0:
            log_to_blender("Auto-imports will begin shortly...")
        else:
            log_to_blender("No outputs found for auto-import")


classes = [
    RUNCHAT_OT_execute,
]