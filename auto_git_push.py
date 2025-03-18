#!/usr/bin/env python
"""
Auto Git Push - Watches for file changes and automatically commits and pushes to GitHub.
This script helps keep your GitHub repository updated automatically.

Usage:
    python auto_git_push.py [OPTIONS]

Options:
    --watch_dir DIRECTORY    Directory to watch for changes (default: current directory)
    --interval SECONDS       Check interval in seconds (default: 60)
    --message MESSAGE        Custom commit message (default: "Auto update: {timestamp}")
"""

import os
import subprocess
import time
import argparse
from datetime import datetime
import sys

def run_command(command):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True, shell=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_git_status():
    """Check if there are any changes to commit"""
    success, output = run_command("git status --porcelain")
    return success and output.strip() != ""

def git_add_all():
    """Add all changes to git staging"""
    return run_command("git add .")

def git_commit(message):
    """Commit changes with the provided message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "{timestamp}" in message:
        message = message.replace("{timestamp}", timestamp)
    return run_command(f'git commit -m "{message}"')

def git_push():
    """Push changes to the remote repository"""
    return run_command("git push")

def check_git_repo():
    """Check if the current directory is a git repository"""
    return run_command("git rev-parse --is-inside-work-tree")

def setup_git_credentials():
    """Set up credential caching to avoid repeated password prompts"""
    run_command("git config --global credential.helper cache")
    run_command("git config --global credential.helper 'cache --timeout=3600'")

def main():
    parser = argparse.ArgumentParser(description="Auto Git Push - Automatically commit and push changes to GitHub")
    parser.add_argument("--watch_dir", default=".", help="Directory to watch for changes")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--message", default="Auto update: {timestamp}", help="Custom commit message")
    
    args = parser.parse_args()
    
    os.chdir(args.watch_dir)
    
    # Check if we're in a git repository
    success, _ = check_git_repo()
    if not success:
        print("Error: Not a git repository. Please run this script in a git repository.")
        sys.exit(1)
    
    # Setup git credentials caching
    setup_git_credentials()
    
    print(f"Watching directory: {os.path.abspath(args.watch_dir)}")
    print(f"Check interval: {args.interval} seconds")
    print(f"Commit message template: {args.message}")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            if check_git_status():
                print(f"Changes detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                success, output = git_add_all()
                if not success:
                    print(f"Error adding files: {output}")
                    continue
                
                success, output = git_commit(args.message)
                if not success:
                    print(f"Error committing changes: {output}")
                    continue
                
                print(f"Committed changes: {output.strip()}")
                
                success, output = git_push()
                if not success:
                    print(f"Error pushing changes: {output}")
                    continue
                
                print(f"Successfully pushed changes to GitHub")
            
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopping auto git push")

if __name__ == "__main__":
    main() 