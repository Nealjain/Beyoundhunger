#!/usr/bin/env python3
"""
Fix backslash errors in Python files
This script fixes incorrect backslashes that cause syntax errors
"""
import os
import re

def fix_file(file_path):
    """Fix specific backslash errors in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Fix backslash at end of line
        pattern = r'(.*?)\\(\s*\n)'
        
        # Replace with valid continuation
        def replacer(match):
            return match.group(1) + match.group(2)
        
        new_content = re.sub(pattern, replacer, content)
        
        if new_content != content:
            print(f"Fixing backslash errors in {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

# Specify files to fix
file_paths = [
    "food_donation/views.py",
    "food_donation/models.py",
    "food_donation/forms.py"
]

# Fix each file
fixed_count = 0
for file_path in file_paths:
    if os.path.exists(file_path) and fix_file(file_path):
        fixed_count += 1

print(f"Fixed backslash errors in {fixed_count} files")
print("\nNow try running these commands again:")
print("python manage.py migrate")
print("python manage.py collectstatic --noinput") 