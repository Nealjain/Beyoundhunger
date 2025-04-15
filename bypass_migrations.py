#!/usr/bin/env python3
"""
This script bypasses form validation errors to allow migrations to run.
It temporarily modifies system paths to prevent form errors from blocking migrations.
"""

import os
import sys
import importlib
import django
from django.core.management import call_command

def run_migrations():
    print("Setting up environment to bypass form errors...")
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beyond_hunger.settings')
    
    # Bypass form imports
    import builtins
    original_import = builtins.__import__
    
    def patched_import(name, *args, **kwargs):
        # Block problematic form imports during initial loading
        if name == 'food_donation.forms' and 'food_donation.views' in sys.modules:
            print(f"⚠️ Bypassing import of {name}")
            module = type(sys)(name)
            sys.modules[name] = module
            return module
        return original_import(name, *args, **kwargs)
    
    # Apply the patch
    builtins.__import__ = patched_import
    
    # Initialize Django
    try:
        django.setup()
        print("✅ Django initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Django: {e}")
        return False
    
    # Run migrations
    try:
        call_command('migrate')
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
    finally:
        # Restore original import function
        builtins.__import__ = original_import

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1) 