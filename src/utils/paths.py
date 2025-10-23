import os
import sys

def resource_path(relative_path):
    """Get actual resource path for packaged or development stage"""
    # Check if path needs conversion
    if relative_path.startswith("config/"):
        # Map config/ path to new directory structure
        parts = relative_path.split("/", 1)
        if len(parts) > 1:
            file_path = parts[1]
            # Decide which directory to map to based on file extension
            if file_path.endswith(".jsl"):
                relative_path = f"scripts/jsl/{file_path}"
            elif file_path.endswith(".md"):
                relative_path = f"docs/{file_path}"
    
    # Return final path
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), relative_path)