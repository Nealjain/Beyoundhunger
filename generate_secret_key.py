#!/usr/bin/env python3
"""
Generate a secure secret key for Django.
Run this script to generate a new secret key that you can use in your Django project.
"""
import secrets
import string

def generate_secret_key(length=50):
    """Generate a secure random string suitable for Django secret key."""
    chars = string.ascii_letters + string.digits + string.punctuation
    # Filter out characters that might cause problems in environment variables
    chars = chars.replace("'", "").replace('"', "").replace('\\', "").replace('$', "")
    return ''.join(secrets.choice(chars) for _ in range(length))

if __name__ == "__main__":
    key = generate_secret_key()
    print("\nGenerated Django Secret Key:")
    print("-" * 60)
    print(key)
    print("-" * 60)
    print("\nAdd this to your environment variables as DJANGO_SECRET_KEY")
    print("For PythonAnywhere, add to your wsgi file:\n")
    print(f"os.environ['DJANGO_SECRET_KEY'] = '{key}'")
    print("-" * 60) 