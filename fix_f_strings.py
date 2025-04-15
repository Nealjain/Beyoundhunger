#!/usr/bin/env python3
"""
Fix f-strings with backslashes in the project
"""
import os
import re

def fix_file(file_path):
    """Fix f-strings in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Pattern for f-strings with backslashes
        pattern = r'f(["\'])(.*?\\.*?)(\1)'
        
        # Replace backslashes with double backslashes in f-strings
        def replacer(match):
            quote = match.group(1)
            content = match.group(2).replace('\\', '\\\\')
            return f'f{quote}{content}{quote}'
        
        new_content = re.sub(pattern, replacer, content)
        
        if new_content != content:
            print(f"Fixing f-strings in {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def fix_directory(directory):
    """Recursively fix f-strings in all Python files in a directory"""
    fixed_files = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_file(file_path):
                    fixed_files += 1
    return fixed_files

if __name__ == "__main__":
    # Fix all Python files in the current directory
    fixed_count = fix_directory(".")
    print(f"Fixed f-strings in {fixed_count} files") 