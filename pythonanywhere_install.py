#!/usr/bin/env python3
"""
Script to install minimal packages on PythonAnywhere
This script installs packages one by one to avoid timeouts
"""

import subprocess
import sys
import time

def run_command(command):
    """Run a command and return its output"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"STDERR: {e.stderr}")
        return False

def install_packages():
    """Install essential packages one by one"""
    packages = [
        "Django>=5.0.0,<5.2.0",
        "pillow>=10.0.0,<12.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "django-allauth>=0.58.0,<0.60.0",
        "djangorestframework>=3.14.0,<4.0.0",
    ]
    
    for package in packages:
        print(f"\n{'='*50}\nInstalling {package}\n{'='*50}")
        success = run_command(f"pip install {package}")
        if not success:
            print(f"Failed to install {package}. Continuing with next package.")
        # Sleep to avoid overwhelming PythonAnywhere
        time.sleep(2)

if __name__ == "__main__":
    print("Starting minimal package installation for PythonAnywhere...")
    install_packages()
    print("Installation process completed!") 