#!/usr/bin/env python
"""
Django Secret Key Generator
"""
from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    # Generate a secure secret key
    secret_key = get_random_secret_key()
    print("\nGenerated Django SECRET_KEY for production use:")
    print("-" * 60)
    print(f"{secret_key}")
    print("-" * 60)
    
    print("\nCopy this value and use it in your PythonAnywhere WSGI file for the DJANGO_SECRET_KEY environment variable.\n") 