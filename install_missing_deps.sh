#!/bin/bash
# Script to install missing dependencies for Beyond Hunger project

echo "=== Installing Missing Dependencies ==="

# Essential system packages
echo "Installing required system packages..."
pip install wheel setuptools

# Google OAuth dependencies
echo "Installing Google OAuth dependencies..."
pip install cryptography
pip install pyjwt

# Database dependencies
echo "Installing database dependencies..."
pip install dj-database-url

# PDF support
echo "Installing PDF generation libraries..."
pip install reportlab

# Fixing common dependency issues
echo "Installing other common dependencies..."
pip install six
pip install certifi
pip install cffi
pip install charset-normalizer
pip install idna
pip install urllib3

echo "=== Dependencies Installation Complete ==="
echo "Run your migration command again: python manage.py migrate" 