#!/usr/bin/env python3
"""
Setup script for PythonAnywhere deployment
This script prepares directories and database for deployment
"""
import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories if they don't exist"""
    print("Creating necessary directories...")
    
    directories = [
        'static',
        'media',
        'media/donations',
        'media/profile_pics',
        'media/id_verification',
        'media/marketplace'
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            print(f"Creating {directory}/ directory")
            path.mkdir(parents=True, exist_ok=True)
    
    print("✓ Directories created successfully")

def check_database():
    """Check if database file exists and is accessible"""
    print("Checking database...")
    
    db_path = Path('db.sqlite3')
    if db_path.exists():
        print(f"✓ Database found at {db_path}")
        print(f"  Size: {db_path.stat().st_size / 1024:.2f} KB")
    else:
        print("× Database not found! Migrations need to be run.")
        print("  Run: python manage.py migrate")

def check_environment():
    """Check the environment setup"""
    print("Checking environment...")
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"✓ Python version: {python_version}")
    
    # Check Django version
    try:
        import django
        print(f"✓ Django version: {django.get_version()}")
    except ImportError:
        print("× Django not installed! Run: pip install Django")
    
    # Check for virtualenv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"✓ Virtualenv detected: {sys.prefix}")
    else:
        print("× Not running in a virtualenv! Create one with: mkvirtualenv <name>")

def main():
    """Main function"""
    print("=== PythonAnywhere Setup ===")
    
    check_environment()
    create_directories()
    check_database()
    
    print("\nSetup completed! Next steps:")
    print("1. Configure your Web app in the PythonAnywhere Web tab")
    print("2. Set up your WSGI file using pythonanywhere_wsgi.py")
    print("3. Ensure static files are configured correctly")
    print("4. Reload your Web app")

if __name__ == "__main__":
    main() 