#!/usr/bin/env python3
"""
This script automatically updates form fields to match model fields.
It will create a backup of your forms.py file before making changes.
"""

import os
import sys
import re
import django
import inspect
from datetime import datetime
from django.forms import ModelForm
from shutil import copy2

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beyond_hunger.settings')
    django.setup()

def get_model_fields(model_class):
    """Get all field names from a model class."""
    return [field.name for field in model_class._meta.get_fields() 
            if not (field.many_to_many and field.auto_created) and not field.one_to_many]

def update_forms():
    """Update form fields to match model fields."""
    setup_django()
    
    # Get the path to forms.py
    from food_donation import forms
    forms_path = inspect.getfile(forms)
    
    # Create a backup
    backup_path = f"{forms_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    copy2(forms_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    # Read the forms file
    with open(forms_path, 'r') as f:
        content = f.read()
    
    form_classes = []
    for name, obj in inspect.getmembers(forms):
        if inspect.isclass(obj) and issubclass(obj, ModelForm) and obj != ModelForm:
            form_classes.append((name, obj))
    
    print(f"Found {len(form_classes)} model forms to update")
    
    for name, form_class in form_classes:
        if not hasattr(form_class.Meta, 'model') or not hasattr(form_class.Meta, 'fields'):
            print(f"⚠️ Skipping {name} - missing Meta.model or Meta.fields")
            continue
        
        model_class = form_class.Meta.model
        model_fields = get_model_fields(model_class)
        form_fields = getattr(form_class.Meta, 'fields', [])
        
        # Skip '__all__'
        if form_fields == '__all__':
            continue
        
        # Find invalid fields
        invalid_fields = [field for field in form_fields if field not in model_fields]
        
        if not invalid_fields:
            print(f"✅ {name} is already valid")
            continue
        
        print(f"🔄 Updating {name} - removing fields: {', '.join(invalid_fields)}")
        
        # Create new list of valid fields
        valid_fields = [field for field in form_fields if field in model_fields]
        
        # Build new fields list representation
        new_fields_str = "[\n            '" + "',\n            '".join(valid_fields) + "'\n        ]"
        
        # Find the class definition in the content
        class_pattern = rf"class\s+{name}\s*\(\s*forms\.ModelForm\s*\)\s*:"
        class_match = re.search(class_pattern, content)
        
        if not class_match:
            print(f"⚠️ Could not find class definition for {name}")
            continue
        
        # Find the fields list in the class
        fields_pattern = r"fields\s*=\s*\[(.*?)\]"
        # Use re.DOTALL to match across multiple lines
        fields_match = re.search(fields_pattern, content[class_match.end():], re.DOTALL)
        
        if not fields_match:
            print(f"⚠️ Could not find fields list for {name}")
            continue
        
        # Replace the fields list
        start_pos = class_match.end() + fields_match.start()
        end_pos = class_match.end() + fields_match.end()
        
        content = (
            content[:start_pos] + 
            "fields = " + new_fields_str + 
            content[end_pos:]
        )
    
    # Write the updated content
    with open(forms_path, 'w') as f:
        f.write(content)
    
    print("\nForms updated successfully! 🎉")
    print(f"A backup was created at {backup_path}")
    return True

if __name__ == "__main__":
    success = update_forms()
    sys.exit(0 if success else 1) 