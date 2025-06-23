# api.py

import requests
import bpy


def log_to_blender(message, level='INFO'):
    """Log message to Blender's Info log"""
    print(f"[Runchat API] {message}")
    # API module doesn't have operator context, so just print to console


class RunChatAPI:
    BASE_URL = "https://runchat.app/api/v1"
    UPLOAD_URL = "https://runchat.app/api/upload/supabase"
    
    @staticmethod
    def get_headers(api_key):
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    @staticmethod
    def get_schema(runchat_id, api_key):
        """Get schema for a Runchat workflow"""
        if not runchat_id or not api_key:
            log_to_blender("Runchat ID and API key are required", 'ERROR')
            return None
        
        url = f"{RunChatAPI.BASE_URL}/{runchat_id}/schema"
        headers = RunChatAPI.get_headers(api_key)
        
        log_to_blender(f"Making API request to: {url}")
        log_to_blender(f"Headers: {headers}")
        
        try:
            log_to_blender("Sending GET request for schema...")
            response = requests.get(url, headers=headers, timeout=30)
            log_to_blender(f"Response status: {response.status_code}")
            log_to_blender(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            result = response.json()
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
        
        try:
            log_to_blender("Sending POST request...")
            response = requests.post(url, headers=headers, json=data, timeout=180)  # Increased timeout
            
            log_to_blender(f"Response received - Status: {response.status_code}")
            log_to_blender(f"Response headers: {dict(response.headers)}")
            log_to_blender(f"Response content length: {len(response.text)}")
            
            if response.status_code != 200:
                log_to_blender(f"Non-200 status code: {response.status_code}", 'ERROR')
                log_to_blender(f"Response text: {response.text}", 'ERROR')
            
            response.raise_for_status()
            
            try:
                result = response.json()
                log_to_blender("Response parsed successfully")
                log_to_blender(f"Result type: {type(result)}")
                if isinstance(result, dict):
                    log_to_blender(f"Result keys: {list(result.keys())}")
                    if 'outputs' in result:
                        log_to_blender(f"Found {len(result['outputs'])} outputs")
                        for key, value in result['outputs'].items():
                            log_to_blender(f"  Output '{key}': {type(value).__name__} = {str(value)[:100]}...")
                    if 'instance_id' in result:
                        log_to_blender(f"Instance ID: {result['instance_id']}")
                else:
                    log_to_blender(f"Result content: {result}")
                return result
            except ValueError as json_error:
                log_to_blender(f"JSON decode error: {json_error}", 'ERROR')
                log_to_blender(f"Raw response (first 500 chars): {response.text[:500]}", 'ERROR')
                return None
                
        except requests.exceptions.Timeout:
            log_to_blender("Request timed out after 180 seconds", 'ERROR')
            return None
        except requests.exceptions.ConnectionError as e:
            log_to_blender(f"Connection error: {e}", 'ERROR')
            return None
        except requests.exceptions.HTTPError as e:
            log_to_blender(f"HTTP Error: {e}", 'ERROR')
            log_to_blender(f"Response content: {response.text}", 'ERROR')
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
        
        data = {
            "base64Image": base64_image,
            "filename": filename
        }
        
        log_to_blender(f"Uploading image: {filename}")
        log_to_blender(f"Image size: {len(base64_image)} characters")
        
        try:
            log_to_blender("Sending image upload request...")
            response = requests.post(url, headers=headers, json=data, timeout=60)
            log_to_blender(f"Upload response status: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            url_result = result.get("url")
            if url_result:
                log_to_blender(f"Image uploaded successfully: {url_result}")
            else:
                log_to_blender("Image upload completed but no URL returned", 'WARNING')
            
            return url_result
        except requests.exceptions.RequestException as e:
            log_to_blender(f"Image upload error: {e}", 'ERROR')
            if hasattr(e, 'response') and e.response is not None:
                log_to_blender(f"Response content: {e.response.text}", 'ERROR')
            return None