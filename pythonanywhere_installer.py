#!/usr/bin/env python
"""
PythonAnywhere Package Installer Helper Script
This script installs packages one at a time to avoid timeouts on PythonAnywhere.
"""

import os
import sys
import subprocess
import time

def install_package(package):
    """Install a single package"""
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    """Main function to install all packages from minimal_requirements.txt"""
    # Check if the file exists
    if not os.path.exists("minimal_requirements.txt"):
        print("Error: minimal_requirements.txt not found.")
        print("Please upload this file to your PythonAnywhere account.")
        return 1
    
    # Read the requirements file
    with open("minimal_requirements.txt", "r") as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    # Install each package with a delay in between
    success_count = 0
    fail_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
        else:
            fail_count += 1
        
        # Add a delay to avoid overwhelming the system
        time.sleep(1)
    
    print("\n==================================")
    print(f"Installation complete: {success_count} packages installed successfully")
    if fail_count > 0:
        print(f"Warning: {fail_count} packages failed to install")
    print("==================================")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 