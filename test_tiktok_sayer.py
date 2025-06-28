#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for TikTok-Sayer
This script checks if all required dependencies are installed and if the application can be launched.
"""

import sys
import importlib
import subprocess
import os


def check_dependency(module_name, package_name=None):
    """Check if a Python module is installed"""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed. Install it with: pip install {package_name}")
        return False


def main():
    """Main function to test TikTok-Sayer dependencies"""
    print("\n=== TikTok-Sayer Dependency Test ===\n")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 6:
        print(f"✅ Python version {python_version.major}.{python_version.minor}.{python_version.micro} is compatible")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor}.{python_version.micro} is NOT compatible. Python 3.6+ is required.")
        return False
    
    # Check required dependencies
    dependencies = [
        ("requests", None),
        ("tkinter", "tk"),
        ("PIL", "pillow"),
        ("customtkinter", None),
        ("dotenv", "python-dotenv"),
        ("requests_html", "requests-html"),
        ("bs4", "beautifulsoup4"),
        ("fake_useragent", "fake-useragent")
    ]
    
    all_installed = True
    for module_name, package_name in dependencies:
        if not check_dependency(module_name, package_name):
            all_installed = False
    
    # Check if main script exists
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_sayer.py")
    if os.path.exists(script_path):
        print(f"✅ Main script found at {script_path}")
    else:
        print(f"❌ Main script NOT found at {script_path}")
        all_installed = False
    
    print("\n=== Test Results ===\n")
    if all_installed:
        print("All dependencies are installed! You can run TikTok-Sayer with:")
        print("  python tiktok_sayer.py")
        print("\nOr use the provided batch/shell script:")
        if os.name == 'nt':  # Windows
            print("  run_tiktok_sayer.bat")
        else:  # Unix/Linux/Mac
            print("  ./run_tiktok_sayer.sh")
        
        # Try to import the main module without running it
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            importlib.import_module("tiktok_sayer")
            print("\n✅ TikTok-Sayer module can be imported successfully")
        except Exception as e:
            print(f"\n❌ Error importing TikTok-Sayer module: {str(e)}")
            all_installed = False
    else:
        print("Some dependencies are missing. Please install them using:")
        print("  pip install -r requirements.txt")
    
    return all_installed


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)