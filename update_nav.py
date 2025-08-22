#!/usr/bin/env python3

import os
import re

# List of files to update
files_to_update = [
    "pages/4_Weather.py",
    "pages/5_Ranges.py", 
    "pages/6_Rifles.py",
    "pages/7_Cartridges.py",
    "pages/9_Bullets.py",
    "pages/10_Admin.py"
]

for file_path in files_to_update:
    if os.path.exists(file_path):
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Remove the top-level navigation import
        content = re.sub(r'\n# Import custom navigation\nimport navigation\n', '', content)
        
        # Add navigation import after page config
        content = re.sub(
            r'(st\.set_page_config\([^)]+\))',
            r'\1\n\n    # Import custom navigation AFTER page config\n    import navigation',
            content
        )
        
        # Write the file back
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Updated {file_path}")
    else:
        print(f"File not found: {file_path}")
