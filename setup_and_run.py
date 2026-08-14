#!/usr/bin/env python3
"""
Setup and run script for Virtual Keyboard Mouse
This script handles package installation and runs the application
"""
import subprocess
import sys
import os

# Add current directory to path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Try to import required packages
required_packages = {
    'cv2': 'opencv-python>=4.5.0',
    'numpy': 'numpy>=1.19.0',
    'cvzone': 'cvzone>=1.5.0',
    'pynput': 'pynput>=1.7.0',
    'pyautogui': 'pyautogui>=0.9.50',
    'mediapipe': 'mediapipe>=0.8.0'
}

print("Checking for required packages...")
missing_packages = []

for module, package in required_packages.items():
    try:
        __import__(module)
        print(f"✓ {module} is installed")
    except ImportError:
        print(f"✗ {module} is NOT installed")
        missing_packages.append(package)

if missing_packages:
    print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
    for package in missing_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")

print("\nAll packages ready. Starting application...")
print("-" * 50)

# Now run the main application
try:
    exec(open('main.py').read())
except Exception as e:
    print(f"Error running application: {e}")
    sys.exit(1)
