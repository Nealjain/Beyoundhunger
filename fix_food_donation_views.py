#!/usr/bin/env python3
"""
Comprehensive fix script for views.py
This fixes both backslash and indentation errors
"""
import os
import re

def fix_marketplace_items_query(content):
    """Fix the specific error in the marketplace items query."""
    # The pattern we're looking for is like:
    # items = MarketplaceItem.objects.filter(status='available')\\
    #    .select_related('seller')\
    
    # Replace with properly formatted query
    pattern = r"items = MarketplaceItem\.objects\.filter\(status='available'\)\\\\(\s*)\n(\s*)\.select_related\('seller'\)\\"
    replacement = r"items = MarketplaceItem.objects.filter(status='available')\1\n\2.select_related('seller')"
    
    return re.sub(pattern, replacement, content)

def fix_all_continuations(content):
    """Fix all line continuation issues."""
    # Fix all trailing backslashes at line ends (improper continuation)
    content = re.sub(r'\\(\s*\n)', r'\1', content)
    
    # Fix indentation after proper continuations
    lines = content.splitlines()
    result_lines = []
    continued = False
    
    for i, line in enumerate(lines):
        if i > 0 and continued and line.strip() and line[0] != ' ' and not line.strip().startswith('#'):
            # This line should be indented after a continuation
            result_lines.append('    ' + line)
        else:
            result_lines.append(line)
        
        # Check if this line has a proper continuation
        continued = line.strip().endswith('\\')
    
    return '\n'.join(result_lines)

def fix_views_file():
    """Fix the views.py file."""
    views_path = "food_donation/views.py"
    if not os.path.exists(views_path):
        print(f"Error: {views_path} not found!")
        return False
    
    print(f"Reading {views_path}...")
    with open(views_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Make a backup
    with open(f"{views_path}.bak", 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup created at {views_path}.bak")
    
    # Fix the specific marketplace items query
    new_content = fix_marketplace_items_query(content)
    
    # Fix all other continuation issues
    new_content = fix_all_continuations(new_content)
    
    if new_content != content:
        print(f"Fixing syntax errors in {views_path}")
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    print("No issues found that need fixing.")
    return False

if __name__ == "__main__":
    print("=== Starting comprehensive fixes for views.py ===")
    if fix_views_file():
        print("\n✅ Fixes applied successfully!")
    else:
        print("\n❌ No changes were made. Perhaps the file doesn't need fixing?")
    
    print("\nNow try running these commands again:")
    print("python manage.py migrate")
    print("python manage.py collectstatic --noinput") 