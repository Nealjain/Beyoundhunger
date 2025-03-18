#!/usr/bin/env python3
"""
Run script for Beyond Hunger Analytics Dashboard
This script checks for required dependencies and launches the analytics application.
"""

import sys
import subprocess
import importlib.util

def check_dependency(package):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package)
    if spec is None:
        print(f"Missing dependency: {package}")
        print(f"Please install it using: pip install {package}")
        return False
    return True

def main():
    """Main function to run the analytics dashboard"""
    # Check required dependencies
    required_packages = ['PyQt6']
    missing_deps = False
    
    for package in required_packages:
        if not check_dependency(package):
            missing_deps = True
    
    if missing_deps:
        print("\nPlease install all required dependencies using:")
        print("pip install PyQt6")
        return 1
    
    # Try to run the full analytics app if all dependencies are available
    try:
        import matplotlib
        import pandas
        import numpy
        import reportlab
        import openpyxl
        
        print("Starting Beyond Hunger Analytics Dashboard with full features...")
        from analytics_app import BeyondHungerAnalytics, QApplication
        app = QApplication(sys.argv)
        window = BeyondHungerAnalytics()
        window.show()
        return app.exec()
    except ImportError:
        # Fall back to simple version if dependencies are missing
        print("Some dependencies are missing. Starting simple version...")
        try:
            from simple_analytics import SimpleAnalyticsDashboard, QApplication
            app = QApplication(sys.argv)
            window = SimpleAnalyticsDashboard()
            window.show()
            return app.exec()
        except Exception as e:
            print(f"Error starting application: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main()) 