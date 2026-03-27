from string import *

import base64

def safe_to_string(data: bytes | str) -> str:
    if isinstance(data, str):
        return data
    if isinstance(data, bytes):
        try:
            return data.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            encoded = base64.b64encode(data).decode('ascii')
            return f"(base64_encoded={encoded})"
    
    try:
        return str(data)
    except Exception:
        return "[unconvertible object]"