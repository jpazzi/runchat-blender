# utils/data_utils.py

import re
from typing import Any, Dict, Optional


def extract_socket_value(socket) -> Any:
    """Extract value from a Blender node socket"""
    try:
        if hasattr(socket, 'default_value'):
            default_value = socket.default_value
            
            # Handle different socket types
            if hasattr(default_value, '__len__') and not isinstance(default_value, str):
                # Vector, Color, or array-like
                return list(default_value)
            else:
                # Scalar value
                return default_value
        else:
            # Socket without default value
            return None
    except Exception as e:
        print(f"Error extracting socket value: {e}")
        return None


def format_data_for_runchat(data: Any, data_type: str = 'auto') -> Any:
    """Format data for RunChat API consumption"""
    try:
        if data is None:
            return None
        
        # Auto-detect type if not specified
        if data_type == 'auto':
            if isinstance(data, (int, float)):
                data_type = 'number'
            elif isinstance(data, str):
                data_type = 'string'
            elif isinstance(data, (list, tuple)):
                data_type = 'array'
            elif isinstance(data, dict):
                data_type = 'object'
            elif isinstance(data, bool):
                data_type = 'boolean'
            else:
                data_type = 'string'  # Fallback to string
        
        # Format based on type
        if data_type == 'number':
            return float(data) if '.' in str(data) else int(data)
        elif data_type == 'string':
            return str(data)
        elif data_type == 'boolean':
            return bool(data)
        elif data_type == 'array':
            if isinstance(data, (list, tuple)):
                return [format_data_for_runchat(item) for item in data]
            else:
                return [data]  # Wrap single value in array
        elif data_type == 'object':
            if isinstance(data, dict):
                return {k: format_data_for_runchat(v) for k, v in data.items()}
            else:
                return {'value': data}  # Wrap in object
        else:
            # Fallback to string representation
            return str(data)
            
    except Exception as e:
        print(f"Error formatting data: {e}")
        return str(data)  # Fallback to string


def process_runchat_output(output_data: Dict[str, Any]) -> Any:
    """Process output data from RunChat API"""
    try:
        if not isinstance(output_data, dict):
            return output_data
        
        # Check for common output patterns
        if 'data' in output_data:
            return output_data['data']
        elif 'value' in output_data:
            return output_data['value']
        elif 'result' in output_data:
            return output_data['result']
        elif 'output' in output_data:
            return output_data['output']
        else:
            # Return the whole object if no standard key found
            return output_data
            
    except Exception as e:
        print(f"Error processing output data: {e}")
        return output_data


def validate_workflow_id(workflow_id: str) -> bool:
    """Validate a RunChat workflow ID format"""
    try:
        if not workflow_id or not isinstance(workflow_id, str):
            return False
        
        # Remove whitespace
        workflow_id = workflow_id.strip()
        
        # Check if it's a valid UUID or similar ID format
        # Accept alphanumeric with hyphens, underscores, or dots
        pattern = r'^[a-zA-Z0-9._-]+$'
        
        if not re.match(pattern, workflow_id):
            return False
        
        # Check reasonable length (between 5 and 100 characters)
        if len(workflow_id) < 5 or len(workflow_id) > 100:
            return False
        
        return True
        
    except Exception as e:
        print(f"Error validating workflow ID: {e}")
        return False


def handle_tree_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle hierarchical tree data structures"""
    try:
        if not isinstance(data, dict):
            return {}
        
        # Extract relevant data from tree structure
        result = {}
        
        # Look for common tree patterns
        if 'nodes' in data and isinstance(data['nodes'], dict):
            for node_id, node_data in data['nodes'].items():
                if isinstance(node_data, dict):
                    # Extract node outputs
                    if 'outputs' in node_data:
                        for output_key, output_value in node_data['outputs'].items():
                            result[f"{node_id}_{output_key}"] = output_value
                    # Extract node values
                    elif 'value' in node_data:
                        result[node_id] = node_data['value']
        
        # Look for flat structure
        elif 'outputs' in data:
            result.update(data['outputs'])
        
        # Look for direct key-value pairs
        else:
            for key, value in data.items():
                if not key.startswith('_'):  # Skip internal keys
                    result[key] = value
        
        return result
        
    except Exception as e:
        print(f"Error handling tree data: {e}")
        return {}


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe file system use"""
    try:
        if not filename:
            return "unnamed_file"
        
        # Remove or replace problematic characters
        # Keep alphanumeric, hyphens, underscores, and dots
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores and dots
        sanitized = sanitized.strip('_.')
        
        # Ensure it's not empty after sanitization
        if not sanitized:
            sanitized = "unnamed_file"
        
        # Limit length to reasonable size
        if len(sanitized) > 100:
            # Keep the extension if present
            if '.' in sanitized:
                name, ext = sanitized.rsplit('.', 1)
                sanitized = name[:95] + '.' + ext
            else:
                sanitized = sanitized[:100]
        
        return sanitized
        
    except Exception as e:
        print(f"Error sanitizing filename: {e}")
        return "unnamed_file"


def parse_json_safely(json_string: str) -> Optional[Dict]:
    """Safely parse JSON string with error handling"""
    try:
        import json
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing JSON: {e}")
        return None


def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    try:
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
        
    except Exception as e:
        print(f"Error merging dictionaries: {e}")
        return dict1


def validate_api_response(response: Dict) -> bool:
    """Validate that an API response has expected structure"""
    try:
        if not isinstance(response, dict):
            return False
        
        # Check for error indicators
        if 'error' in response and response['error']:
            print(f"API Error: {response.get('error')}")
            return False
        
        # Check for required fields (basic validation)
        if 'data' not in response and 'outputs' not in response:
            print("API response missing data/outputs")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error validating API response: {e}")
        return False


def extract_urls_from_text(text: str) -> list:
    """Extract URLs from text"""
    try:
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls
    except Exception as e:
        print(f"Error extracting URLs: {e}")
        return []


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}"
        
    except Exception as e:
        print(f"Error formatting file size: {e}")
        return f"{size_bytes} B" 