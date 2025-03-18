#!/usr/bin/env python
"""
Simple starter script for the auto_git_push.py tool.
This makes it easier to run the auto-push feature with common options.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Start the auto git push feature")
    parser.add_argument("--interval", type=int, default=30, 
                        help="Check interval in seconds (default: 30)")
    parser.add_argument("--message", default="Auto update: {timestamp}", 
                        help="Custom commit message (default: 'Auto update: {timestamp}')")
    parser.add_argument("--watch", default=".", 
                        help="Directory to watch (default: current directory)")
    args = parser.parse_args()
    
    # Display welcome message
    print("\n===== Beyond Hunger Auto Git Push =====\n")
    print("This tool will automatically commit and push your changes to GitHub.")
    print(f"Watching directory: {os.path.abspath(args.watch)}")
    print(f"Checking for changes every {args.interval} seconds")
    print(f"Using commit message: {args.message}")
    print("\nSetup Steps:")
    
    # Check if git is installed
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE)
        print("✅ Git is installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("❌ Git is not installed or not in PATH. Please install Git.")
        sys.exit(1)
    
    # Check if we're in a git repository
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], 
                      check=True, stdout=subprocess.PIPE)
        print("✅ Git repository detected")
    except subprocess.SubprocessError:
        print("❌ Not in a Git repository. Please run this from your project directory.")
        sys.exit(1)
    
    # Check if auto_git_push.py exists
    if not os.path.exists("auto_git_push.py"):
        print("❌ auto_git_push.py not found in the current directory.")
        sys.exit(1)
    print("✅ auto_git_push.py script found")
    
    # Check if git remote is configured
    try:
        result = subprocess.run(["git", "remote", "-v"], check=True, 
                               text=True, capture_output=True)
        if "origin" in result.stdout:
            print("✅ Git remote 'origin' is configured")
        else:
            print("⚠️ Git remote 'origin' is not configured. You may need to set up your GitHub repository.")
    except subprocess.SubprocessError:
        print("⚠️ Could not check git remote configuration.")
        
    print("\nStarting auto git push...\n")
    print("Press Ctrl+C to stop\n")
    
    # Start the auto_git_push.py script
    command = [
        sys.executable, 
        "auto_git_push.py", 
        "--interval", str(args.interval), 
        "--message", args.message,
        "--watch_dir", args.watch
    ]
    
    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print("\nStopped auto git push")
    except Exception as e:
        print(f"\nError running auto_git_push.py: {e}")

if __name__ == "__main__":
    main() 