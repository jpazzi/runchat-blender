"""
HTTP utilities that work with Blender's built-in Python modules
Provides a requests-like interface using urllib
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import ssl
from typing import Optional, Dict, Any

class Response:
    """Simple response object that mimics requests.Response"""
    def __init__(self, response, url):
        self._response = response
        self.url = url
        self.status_code = response.getcode()
        self.headers = dict(response.info())
        self._content = None
        self._text = None
    
    @property
    def content(self):
        if self._content is None:
            self._content = self._response.read()
        return self._content
    
    @property
    def text(self):
        if self._text is None:
            self._text = self.content.decode('utf-8')
        return self._text
    
    def json(self):
        return json.loads(self.text)
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise urllib.error.HTTPError(
                self.url, self.status_code, 
                f"HTTP {self.status_code}", 
                self.headers, None
            )

def get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
    """Make a GET request using urllib"""
    req = urllib.request.Request(url)
    
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    
    try:
        # Create SSL context that doesn't verify certificates (for simplicity)
        # In production, you might want to handle this more securely
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return Response(response, url)
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to connect to {url}: {e}")

def post(url: str, json_data: Optional[Dict[str, Any]] = None, 
         headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
    """Make a POST request using urllib"""
    
    # Prepare data
    data = None
    if json_data:
        data = json.dumps(json_data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    
    # Set default headers for JSON
    if json_data:
        req.add_header('Content-Type', 'application/json')
    
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    
    try:
        # Create SSL context
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return Response(response, url)
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to connect to {url}: {e}")

# For easier migration, you can also create aliases
class requests:
    """Namespace that mimics the requests module interface"""
    
    @staticmethod
    def get(*args, **kwargs):
        return get(*args, **kwargs)
    
    @staticmethod  
    def post(*args, **kwargs):
        return post(*args, **kwargs)
    
    class exceptions:
        RequestException = urllib.error.URLError
        HTTPError = urllib.error.HTTPError
        ConnectionError = ConnectionError
        Timeout = TimeoutError 