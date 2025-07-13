"""
Dependency management for Runchat Blender addon
Uses wheel-based dependencies managed by Blender's extension system
"""

import sys
import os


def get_requests():
    """Get requests module from wheel"""
    try:
        import requests
        print("[Runchat] Using wheel-based requests library")
        return requests, "wheel"
    except ImportError as e:
        print(f"[Runchat] ERROR: Could not import requests from wheels: {e}")
        print("[Runchat] Make sure the addon includes wheel dependencies and Blender extensions are enabled")
        raise ImportError("Requests wheel not found. Please use a properly bundled version of the addon.")


def get_pil():
    """Get PIL/Pillow module from wheel"""
    try:
        from PIL import Image
        print("[Runchat] Using wheel-based PIL/Pillow library")
        return Image, True
    except ImportError as e:
        print(f"[Runchat] ERROR: Could not import PIL from wheels: {e}")
        print("[Runchat] Make sure the addon includes wheel dependencies and Blender extensions are enabled")
        raise ImportError("PIL wheel not found. Please use a properly bundled version of the addon.")


def get_http_client():
    """Get HTTP client (requests) from wheel"""
    return get_requests()


def check_dependencies():
    """Check and report on wheel-based dependencies"""
    print("[Runchat] Checking wheel-based dependencies...")
    
    results = {}
    
    # Check requests (required)
    try:
        requests, requests_backend = get_requests()
        results['requests'] = requests
        results['requests_backend'] = requests_backend
        print(f"[Runchat] Requests: {requests_backend}")
    except ImportError as e:
        print(f"[Runchat] CRITICAL: Missing requests wheel: {e}")
        raise
    
    # Check PIL (required)
    try:
        pil, pil_available = get_pil()
        results['pil'] = pil
        results['pil_available'] = pil_available
        print(f"[Runchat] PIL/Pillow: {'Available' if pil_available else 'Not available'}")
    except ImportError as e:
        print(f"[Runchat] CRITICAL: Missing PIL wheel: {e}")
        raise
    
    return results 