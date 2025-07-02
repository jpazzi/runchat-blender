"""
Dependency management for Runchat Blender addon
Uses bundled dependencies only
"""

import sys
import os


def get_requests():
    """Get bundled requests module"""
    try:
        import requests
        print("[Runchat] Using bundled requests library")
        return requests, "bundled"
    except ImportError as e:
        print(f"[Runchat] ERROR: Could not import bundled requests: {e}")
        print("[Runchat] Make sure the addon includes bundled dependencies in lib/ folder")
        raise ImportError("Bundled requests library not found. Please use a properly bundled version of the addon.")


def get_pil():
    """Get bundled PIL/Pillow module"""
    try:
        from PIL import Image
        print("[Runchat] Using bundled PIL/Pillow library")
        return Image, True
    except ImportError as e:
        print(f"[Runchat] ERROR: Could not import bundled PIL: {e}")
        print("[Runchat] Make sure the addon includes bundled dependencies in lib/ folder")
        raise ImportError("Bundled PIL library not found. Please use a properly bundled version of the addon.")


def get_http_client():
    """Get bundled HTTP client (requests)"""
    return get_requests()


def check_dependencies():
    """Check and report on bundled dependencies"""
    print("[Runchat] Checking bundled dependencies...")
    
    results = {}
    
    # Check requests (required)
    try:
        requests, requests_backend = get_requests()
        results['requests'] = requests
        results['requests_backend'] = requests_backend
        print(f"[Runchat] Requests: {requests_backend}")
    except ImportError as e:
        print(f"[Runchat] CRITICAL: Missing bundled requests: {e}")
        raise
    
    # Check PIL (required)
    try:
        pil, pil_available = get_pil()
        results['pil'] = pil
        results['pil_available'] = pil_available
        print(f"[Runchat] PIL/Pillow: {'Available' if pil_available else 'Not available'}")
    except ImportError as e:
        print(f"[Runchat] CRITICAL: Missing bundled PIL: {e}")
        raise
    
    return results 