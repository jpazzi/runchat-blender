# api.py

import bpy

# Import requests lazily when needed to avoid import issues during module loading
_requests = None

def get_requests_module():
    """Get the requests module, importing it lazily"""
    global _requests
    if _requests is None:
        from .utils.dependencies import get_requests
        _requests, _ = get_requests()
        print("[Runchat API] Using bundled requests library")
    return _requests


def log_to_blender(message, level='INFO'):
    """Log message to Blender's Info log"""
    print(f"[Runchat API] {message}")
    # API module doesn't have operator context, so just print to console


def is_credit_error(error_message):
    """Check if an error message indicates credit exhaustion"""
    if not error_message:
        return False
    
    error_lower = error_message.lower()
    credit_keywords = [
        'credit', 'credits', 'remaining', 'exhausted', 'usage',
        'limit', 'subscription', 'upgrade', 'plan'
    ]
    
    return any(keyword in error_lower for keyword in credit_keywords)


def format_credit_error(error_message):
    """Format a credit error message for display"""
    if not error_message:
        return "No credits remaining to execute this workflow."
    
    # Clean up the error message for better display
    if "This request requires" in error_message or "You have used" in error_message:
        return error_message
    
    return f"Credit limit reached: {error_message}"


class RunChatAPI:
    BASE_URL = "https://runchat.app/api/v1"
    UPLOAD_URL = "https://runchat.app/api/upload/supabase"
    EXAMPLES_URL = "https://runchat.app/api/v1/examples"
    
    @staticmethod
    def get_headers(api_key):
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    @staticmethod
    def get_examples_for_plugin(plugin="blender", version=None):
        """Get curated workflow examples for a specific plugin"""
        url = f"{RunChatAPI.EXAMPLES_URL}?plugin={plugin}"
        if version:
            url += f"&version={version}"
        
        log_to_blender(f"=== FETCHING EXAMPLES ===")
        log_to_blender(f"Plugin: {plugin}")
        log_to_blender(f"URL: {url}")
        
        # Get requests module once and reuse
        requests = get_requests_module()
        
        try:
            log_to_blender("Making request to examples API...")
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate',  # Avoid zstd compression
                'User-Agent': 'Runchat-Blender/1.1.0',
                'Cache-Control': 'no-cache'  # Try to bypass caching
            }
            
            # Use session for better connection handling
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=30)
            log_to_blender(f"Response status: {response.status_code}")
            log_to_blender(f"Response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                log_to_blender(f"Non-200 status code: {response.status_code}", 'ERROR')
                log_to_blender(f"Response text: {response.text}", 'ERROR')
                return None
            
            response.raise_for_status()
            
            # Handle response content more robustly
            try:
                # Check raw content first
                raw_content = response.content
                log_to_blender(f"Raw content length: {len(raw_content)} bytes")
                log_to_blender(f"Content encoding: {response.headers.get('Content-Encoding', 'none')}")
                
                if not raw_content:
                    log_to_blender("Empty raw content received", 'ERROR')
                    return None
                
                # Try to get text content
                try:
                    response_text = response.text
                    log_to_blender(f"Response text length: {len(response_text)}")
                    log_to_blender(f"Response text preview: {response_text[:200]}...")
                except Exception as text_error:
                    log_to_blender(f"Failed to decode response text: {text_error}", 'ERROR')
                    
                    # Fallback: try to decode raw content as UTF-8
                    try:
                        response_text = raw_content.decode('utf-8')
                        log_to_blender(f"Fallback decoded text length: {len(response_text)}")
                        log_to_blender(f"Fallback text preview: {response_text[:200]}...")
                    except Exception as fallback_error:
                        log_to_blender(f"Fallback decode also failed: {fallback_error}", 'ERROR')
                        return None
                
                if not response_text or not response_text.strip():
                    log_to_blender("Empty response text after decoding", 'ERROR')
                    return None
                
                log_to_blender("Parsing JSON response...")
                # Try parsing JSON with error handling
                try:
                    result = response.json()
                except ValueError as json_error:
                    log_to_blender(f"Primary JSON parsing failed: {json_error}", 'ERROR')
                    # Try parsing from the decoded text
                    import json
                    try:
                        result = json.loads(response_text)
                        log_to_blender("Fallback JSON parsing succeeded", 'INFO')
                    except Exception as fallback_json_error:
                        log_to_blender(f"Fallback JSON parsing failed: {fallback_json_error}", 'ERROR')
                        log_to_blender(f"Problem text: {response_text[:500]}", 'ERROR')
                        return None
                        
            except Exception as content_error:
                log_to_blender(f"Error handling response content: {content_error}", 'ERROR')
                return None
            log_to_blender(f"Parsed JSON successfully. Type: {type(result)}")
            
            if isinstance(result, dict):
                log_to_blender(f"Result keys: {list(result.keys())}")
                examples = result.get("examples", [])
                log_to_blender(f"Found {len(examples)} examples for {plugin}")
                
                # Log first example for debugging
                if examples:
                    log_to_blender(f"First example: {examples[0]}")
                
                return result
            else:
                log_to_blender(f"Unexpected result type: {type(result)}", 'ERROR')
                return None
            
        except requests.exceptions.Timeout:
            log_to_blender("Examples request timed out after 30 seconds", 'ERROR')
            return None
        except requests.exceptions.ConnectionError as e:
            log_to_blender(f"Connection error while fetching examples: {e}", 'ERROR')
            return None
        except requests.exceptions.HTTPError as e:
            log_to_blender(f"HTTP Error while fetching examples: {e}", 'ERROR')
            return None
        except requests.exceptions.RequestException as e:
            log_to_blender(f"Request error fetching examples: {e}", 'ERROR')
            return None
        except ValueError as e:
            log_to_blender(f"JSON decode error for examples: {e}", 'ERROR')
            log_to_blender(f"Response text: {response.text}", 'ERROR')
            return None
        except Exception as e:
            log_to_blender(f"Unexpected error fetching examples: {e}", 'ERROR')
            import traceback
            log_to_blender(f"Traceback: {traceback.format_exc()}", 'ERROR')
            return None
    
    @staticmethod
    def get_schema(runchat_id, api_key):
        """Get schema for a Runchat workflow"""
        if not runchat_id or not api_key:
            log_to_blender("Runchat ID and API key are required", 'ERROR')
            return None
        
        url = f"{RunChatAPI.BASE_URL}/{runchat_id}/schema"
        headers = RunChatAPI.get_headers(api_key)
        
        # Add compression headers to avoid zstd
        headers.update({
            'Accept-Encoding': 'gzip, deflate',  # Avoid zstd compression
            'Cache-Control': 'no-cache'  # Try to bypass caching
        })
        
        log_to_blender(f"Making API request to: {url}")
        log_to_blender(f"Headers: {headers}")
        
        # Get requests module once and reuse
        requests = get_requests_module()
        
        try:
            log_to_blender("Sending GET request for schema...")
            response = requests.get(url, headers=headers, timeout=30)
            log_to_blender(f"Response status: {response.status_code}")
            log_to_blender(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # Handle response content robustly (same as examples)
            try:
                # Check raw content first
                raw_content = response.content
                log_to_blender(f"Raw content length: {len(raw_content)} bytes")
                log_to_blender(f"Content encoding: {response.headers.get('Content-Encoding', 'none')}")
                
                if not raw_content:
                    log_to_blender("Empty raw content received", 'ERROR')
                    return None
                
                # Try to get text content
                try:
                    response_text = response.text
                    log_to_blender(f"Response text length: {len(response_text)}")
                except Exception as text_error:
                    log_to_blender(f"Failed to decode response text: {text_error}", 'ERROR')
                    
                    # Fallback: try to decode raw content as UTF-8
                    try:
                        response_text = raw_content.decode('utf-8')
                        log_to_blender(f"Fallback decoded text length: {len(response_text)}")
                    except Exception as fallback_error:
                        log_to_blender(f"Fallback decode also failed: {fallback_error}", 'ERROR')
                        return None
                
                if not response_text or not response_text.strip():
                    log_to_blender("Empty response text after decoding", 'ERROR')
                    return None
                
                # Try parsing JSON with error handling
                try:
                    result = response.json()
                except ValueError as json_error:
                    log_to_blender(f"Primary JSON parsing failed: {json_error}", 'ERROR')
                    # Try parsing from the decoded text
                    import json
                    try:
                        result = json.loads(response_text)
                        log_to_blender("Fallback JSON parsing succeeded", 'INFO')
                    except Exception as fallback_json_error:
                        log_to_blender(f"Fallback JSON parsing failed: {fallback_json_error}", 'ERROR')
                        return None
                        
            except Exception as content_error:
                log_to_blender(f"Error handling response content: {content_error}", 'ERROR')
                return None
            
            log_to_blender(f"Response JSON keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
            log_to_blender("Schema loaded successfully")
            return result
        except requests.exceptions.Timeout:
            log_to_blender("Request timed out after 30 seconds", 'ERROR')
            return None
        except requests.exceptions.ConnectionError:
            log_to_blender("Connection error - check your internet connection", 'ERROR')
            return None
        except requests.exceptions.HTTPError as e:
            log_to_blender(f"HTTP Error: {e}", 'ERROR')
            log_to_blender(f"Response content: {response.text}", 'ERROR')
            return None
        except requests.exceptions.RequestException as e:
            log_to_blender(f"Runchat API Error: {e}", 'ERROR')
            return None
        except ValueError as e:
            log_to_blender(f"JSON decode error: {e}", 'ERROR')
            log_to_blender(f"Response content: {response.text}", 'ERROR')
            return None
    
    @staticmethod
    def run_workflow(runchat_id, api_key, inputs=None, instance_id=None):
        """Run a Runchat workflow"""
        if not runchat_id or not api_key:
            log_to_blender("Runchat ID and API key are required", 'ERROR')
            return None
        
        url = f"{RunChatAPI.BASE_URL}/{runchat_id}"
        headers = RunChatAPI.get_headers(api_key)
        
        # Add compression headers to avoid zstd
        headers.update({
            'Accept-Encoding': 'gzip, deflate',  # Avoid zstd compression
            'Cache-Control': 'no-cache'  # Try to bypass caching
        })
        
        data = {}
        if inputs:
            data["inputs"] = inputs
        if instance_id:
            data["runchat_instance_id"] = instance_id
        
        log_to_blender("=== WORKFLOW EXECUTION API CALL ===")
        log_to_blender(f"URL: {url}")
        log_to_blender(f"Headers: {headers}")
        log_to_blender(f"Data: {data}")
        log_to_blender(f"Payload size: {len(str(data))} characters")
        
        # Get requests module once and reuse
        requests = get_requests_module()
        
        try:
            log_to_blender("Sending POST request...")
            response = requests.post(url, headers=headers, json=data, timeout=300)  # Increased to 5 minutes
            
            log_to_blender(f"Response received - Status: {response.status_code}")
            log_to_blender(f"Response headers: {dict(response.headers)}")
            log_to_blender(f"Response content length: {len(response.text)}")
            
            if response.status_code != 200:
                log_to_blender(f"Non-200 status code: {response.status_code}", 'ERROR')
                log_to_blender(f"Response text: {response.text}", 'ERROR')
            
            response.raise_for_status()
            
            # Handle response content robustly (same as other methods)
            try:
                # Check raw content first
                raw_content = response.content
                log_to_blender(f"Raw content length: {len(raw_content)} bytes")
                log_to_blender(f"Content encoding: {response.headers.get('Content-Encoding', 'none')}")
                
                if not raw_content:
                    log_to_blender("Empty raw content received", 'ERROR')
                    return None
                
                # Try to get text content
                try:
                    response_text = response.text
                    log_to_blender(f"Response text length: {len(response_text)}")
                    log_to_blender(f"Response text preview: {response_text[:200]}...")
                except Exception as text_error:
                    log_to_blender(f"Failed to decode response text: {text_error}", 'ERROR')
                    
                    # Fallback: try to decode raw content as UTF-8
                    try:
                        response_text = raw_content.decode('utf-8')
                        log_to_blender(f"Fallback decoded text length: {len(response_text)}")
                        log_to_blender(f"Fallback text preview: {response_text[:200]}...")
                    except Exception as fallback_error:
                        log_to_blender(f"Fallback decode also failed: {fallback_error}", 'ERROR')
                        return None
                
                if not response_text or not response_text.strip():
                    log_to_blender("Empty response text after decoding", 'ERROR')
                    return None
                
                # Try parsing JSON with error handling
                try:
                    result = response.json()
                    log_to_blender("Primary JSON parsing succeeded", 'INFO')
                except ValueError as json_error:
                    log_to_blender(f"Primary JSON parsing failed: {json_error}", 'ERROR')
                    # Try parsing from the decoded text
                    import json
                    try:
                        result = json.loads(response_text)
                        log_to_blender("Fallback JSON parsing succeeded", 'INFO')
                    except Exception as fallback_json_error:
                        log_to_blender(f"Fallback JSON parsing failed: {fallback_json_error}", 'ERROR')
                        log_to_blender(f"Problem text: {response_text[:500]}", 'ERROR')
                        return None
                        
            except Exception as content_error:
                log_to_blender(f"Error handling response content: {content_error}", 'ERROR')
                return None
            
            log_to_blender("Response parsed successfully")
            log_to_blender(f"Result type: {type(result)}")
            if isinstance(result, dict):
                log_to_blender(f"Result keys: {list(result.keys())}")
                if 'outputs' in result:
                    log_to_blender(f"Found {len(result['outputs'])} outputs")
                    for key, value in result['outputs'].items():
                        log_to_blender(f"  Output '{key}': {type(value).__name__} = {str(value)[:100]}...")
                if 'data' in result:
                    log_to_blender(f"Found 'data' key with type: {type(result['data'])}")
                    if isinstance(result['data'], list):
                        log_to_blender(f"Data array contains {len(result['data'])} items")
                    elif isinstance(result['data'], dict):
                        log_to_blender(f"Data dict contains keys: {list(result['data'].keys())}")
                if 'instance_id' in result:
                    log_to_blender(f"Instance ID: {result['instance_id']}")
            else:
                log_to_blender(f"Result content: {result}")
            return result
                
        except requests.exceptions.Timeout:
            log_to_blender("Request timed out after 5 minutes", 'ERROR')
            return None
        except requests.exceptions.ConnectionError as e:
            log_to_blender(f"Connection error: {e}", 'ERROR')
            return None
        except requests.exceptions.HTTPError as e:
            log_to_blender(f"HTTP Error: {e}", 'ERROR')
            log_to_blender(f"Response content: {response.text}", 'ERROR')
            
            # For 403 errors, try to extract the error message and return it
            if response.status_code == 403:
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and 'error' in error_data:
                        error_message = error_data['error']
                        log_to_blender(f"403 Error details: {error_message}", 'ERROR')
                        # Return a special error result instead of None
                        return {
                            'error': True,
                            'status_code': 403,
                            'message': error_message,
                            'is_credit_error': is_credit_error(error_message)
                        }
                except Exception as parse_error:
                    log_to_blender(f"Failed to parse 403 error response: {parse_error}", 'ERROR')
                    # Return generic credit error for 403s
                    return {
                        'error': True,
                        'status_code': 403,
                        'message': 'Access forbidden - this may be due to insufficient credits.',
                        'is_credit_error': True
                    }
            
            return None
        except requests.exceptions.RequestException as e:
            log_to_blender(f"runchat API Error: {e}", 'ERROR')
            return None

    @staticmethod
    def upload_image(base64_image, filename, api_key):
        """Upload an image to runchat"""
        if not base64_image or not api_key:
            log_to_blender("Base64 image and API key are required", 'ERROR')
            return None
        
        url = RunChatAPI.UPLOAD_URL
        headers = RunChatAPI.get_headers(api_key)
        
        # Add compression headers to avoid zstd
        headers.update({
            'Accept-Encoding': 'gzip, deflate',  # Avoid zstd compression
            'Cache-Control': 'no-cache'  # Try to bypass caching
        })
        
        data = {
            "base64Image": base64_image,
            "filename": filename
        }
        
        log_to_blender(f"Uploading image: {filename}")
        log_to_blender(f"Image size: {len(base64_image)} characters")
        
        # Get requests module once and reuse
        requests = get_requests_module()
        
        try:
            log_to_blender("Sending image upload request...")
            response = requests.post(url, headers=headers, json=data, timeout=60)
            log_to_blender(f"Upload response status: {response.status_code}")
            log_to_blender(f"Upload response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # Handle response content robustly (same as other methods)
            try:
                # Check raw content first
                raw_content = response.content
                log_to_blender(f"Raw content length: {len(raw_content)} bytes")
                log_to_blender(f"Content encoding: {response.headers.get('Content-Encoding', 'none')}")
                
                if not raw_content:
                    log_to_blender("Empty raw content received", 'ERROR')
                    return None
                
                # Try to get text content
                try:
                    response_text = response.text
                    log_to_blender(f"Response text length: {len(response_text)}")
                    log_to_blender(f"Response text preview: {response_text[:200]}...")
                except Exception as text_error:
                    log_to_blender(f"Failed to decode response text: {text_error}", 'ERROR')
                    
                    # Fallback: try to decode raw content as UTF-8
                    try:
                        response_text = raw_content.decode('utf-8')
                        log_to_blender(f"Fallback decoded text length: {len(response_text)}")
                        log_to_blender(f"Fallback text preview: {response_text[:200]}...")
                    except Exception as fallback_error:
                        log_to_blender(f"Fallback decode also failed: {fallback_error}", 'ERROR')
                        return None
                
                if not response_text or not response_text.strip():
                    log_to_blender("Empty response text after decoding", 'ERROR')
                    return None
                
                # Try parsing JSON with error handling
                try:
                    result = response.json()
                    log_to_blender("Upload JSON parsing succeeded", 'INFO')
                except ValueError as json_error:
                    log_to_blender(f"Primary JSON parsing failed: {json_error}", 'ERROR')
                    # Try parsing from the decoded text
                    import json
                    try:
                        result = json.loads(response_text)
                        log_to_blender("Fallback JSON parsing succeeded", 'INFO')
                    except Exception as fallback_json_error:
                        log_to_blender(f"Fallback JSON parsing failed: {fallback_json_error}", 'ERROR')
                        log_to_blender(f"Problem text: {response_text[:500]}", 'ERROR')
                        return None
                        
            except Exception as content_error:
                log_to_blender(f"Error handling response content: {content_error}", 'ERROR')
                return None
            
            url_result = result.get("url")
            if url_result:
                log_to_blender(f"Image uploaded successfully: {url_result}")
            else:
                log_to_blender("Image upload completed but no URL returned", 'WARNING')
            
            return url_result
        except requests.exceptions.Timeout:
            log_to_blender("Upload request timed out", 'ERROR')
            return None
        except requests.exceptions.ConnectionError as e:
            log_to_blender(f"Upload connection error: {e}", 'ERROR')
            return None
        except requests.exceptions.HTTPError as e:
            log_to_blender(f"Upload HTTP Error: {e}", 'ERROR')
            log_to_blender(f"Response content: {response.text}", 'ERROR')
            return None
        except requests.exceptions.RequestException as e:
            log_to_blender(f"Image upload error: {e}", 'ERROR')
            if hasattr(e, 'response') and e.response is not None:
                log_to_blender(f"Response content: {e.response.text}", 'ERROR')
            return None

    @staticmethod
    def poll_workflow_status(runchat_id, api_key, instance_id):
        """Poll for workflow status and progress"""
        if not runchat_id or not api_key or not instance_id:
            log_to_blender("Runchat ID, API key, and instance ID are required for polling", 'ERROR')
            return None
        
        url = f"{RunChatAPI.BASE_URL}/{runchat_id}/status"
        headers = RunChatAPI.get_headers(api_key)
        
        data = {"runchat_instance_id": instance_id}
        
        log_to_blender(f"Polling workflow status - URL: {url}")
        log_to_blender(f"Polling with instance ID: {instance_id}")
        
        try:
            response = get_requests_module().post(url, headers=headers, json=data, timeout=30)
            log_to_blender(f"Polling response status: {response.status_code}")
            
            if response.status_code == 404:
                # Status endpoint might not exist, return None to fall back to regular execution
                return None
            
            response.raise_for_status()
            result = response.json()
            
            log_to_blender(f"Polling result: {result}")
            
            if isinstance(result, dict):
                status = result.get('status', 'unknown')
                progress = result.get('progress', 0)
                log_to_blender(f"Workflow status: {status}, Progress: {progress}")
                return result
            
            return None
            
        except get_requests_module().exceptions.RequestException as e:
            log_to_blender(f"Error polling workflow status: {e}")
            return None