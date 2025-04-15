#!/usr/bin/env python3
"""
Django Setup Helper - Temporarily disables OAuth for initial setup
This script temporarily modifies settings to allow migrations to run without OAuth dependencies
"""
import os
import re
from pathlib import Path

def disable_social_auth():
    """Temporarily disable social auth providers in settings.py"""
    print("Looking for settings.py...")
    
    # Find settings file
    settings_path = None
    for path in [
        Path("beyond_hunger/settings.py"),
        Path("Beyoundhunger/beyond_hunger/settings.py"),
    ]:
        if path.exists():
            settings_path = path
            break
    
    if not settings_path:
        print("Error: Could not find settings.py!")
        return False
    
    print(f"Found settings file at: {settings_path}")
    
    # Read settings file
    with open(settings_path, 'r') as f:
        settings_content = f.read()
    
    # Create backup
    with open(f"{settings_path}.bak", 'w') as f:
        f.write(settings_content)
    print(f"Created backup at: {settings_path}.bak")
    
    # Modify INSTALLED_APPS to comment out social providers
    modified_content = re.sub(
        r"(INSTALLED_APPS\s*=\s*\[\s*(?:['\"].*?['\"]\s*,\s*)*)'allauth\.socialaccount\.providers\.google',",
        r"\1# 'allauth.socialaccount.providers.google',  # Temporarily disabled",
        settings_content
    )
    
    # Modify AUTHENTICATION_BACKENDS to simplify auth
    modified_content = re.sub(
        r"(AUTHENTICATION_BACKENDS\s*=\s*\[\s*).*?\]",
        r"\1'django.contrib.auth.backends.ModelBackend',\n]",
        modified_content, 
        flags=re.DOTALL
    )
    
    # Write modified settings
    with open(settings_path, 'w') as f:
        f.write(modified_content)
    
    print("Modified settings.py to temporarily disable OAuth for initial setup")
    print("You can restore the original file from the backup later")
    return True

def main():
    """Main function"""
    print("=== Django Setup Helper - Temporarily Disabling OAuth ===")
    
    if disable_social_auth():
        print("\nTemporary setup complete! You can now run:")
        print("python manage.py migrate")
        print("python manage.py collectstatic --noinput")
        print("\nAfter setting up, restore the original settings file or")
        print("install all needed dependencies with: ./install_missing_deps.sh")
    else:
        print("\nSetup failed. Try installing dependencies manually:")
        print("pip install cryptography pyjwt")

if __name__ == "__main__":
    main() 