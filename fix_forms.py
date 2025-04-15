#!/usr/bin/env python3
"""
This script finds and fixes form fields that don't match model fields.
Run this to identify and correct form-model mismatches.
"""

import os
import sys
import django
import inspect
from django.apps import apps
from django.db import models
from django.forms import ModelForm

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beyond_hunger.settings')
    django.setup()

def get_model_fields(model_class):
    """Get all field names from a model class."""
    return [field.name for field in model_class._meta.get_fields() 
            if not (field.many_to_many and field.auto_created) and not field.one_to_many]

def check_form(form_class):
    """Check if a form's fields match its model's fields."""
    if not issubclass(form_class, ModelForm) or not hasattr(form_class.Meta, 'model'):
        return True, []  # Not a ModelForm or no model specified
    
    model_class = form_class.Meta.model
    model_fields = get_model_fields(model_class)
    form_fields = getattr(form_class.Meta, 'fields', [])
    
    # Skip '__all__' as it's valid
    if form_fields == '__all__':
        return True, []
    
    # Find fields in form that aren't in model
    invalid_fields = [field for field in form_fields if field not in model_fields]
    
    return len(invalid_fields) == 0, invalid_fields

def scan_and_fix_forms():
    """Scan and fix all form classes in the project."""
    setup_django()
    
    from food_donation import forms
    
    form_classes = []
    for name, obj in inspect.getmembers(forms):
        if inspect.isclass(obj) and issubclass(obj, ModelForm) and obj != ModelForm:
            form_classes.append((name, obj))
    
    print(f"Found {len(form_classes)} model forms to check")
    
    all_valid = True
    for name, form_class in form_classes:
        is_valid, invalid_fields = check_form(form_class)
        if not is_valid:
            all_valid = False
            print(f"❌ {name} has invalid fields: {', '.join(invalid_fields)}")
            # Print the model fields for reference
            model_fields = get_model_fields(form_class.Meta.model)
            print(f"   Available fields for {form_class.Meta.model.__name__}: {', '.join(model_fields)}")
            print(f"   Form fields: {', '.join(getattr(form_class.Meta, 'fields', []))}")
            print()
        else:
            print(f"✅ {name} is valid")
    
    if all_valid:
        print("\nAll forms are valid! 🎉")
    else:
        print("\nSome forms need to be fixed.")
        print("Please update the 'fields' attribute in the Meta class of each form to match the model fields.")
    
    return all_valid

if __name__ == "__main__":
    success = scan_and_fix_forms()
    sys.exit(0 if success else 1) 