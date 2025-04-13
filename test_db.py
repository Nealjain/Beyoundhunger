#!/usr/bin/env python3
"""
Database connectivity test script.
Run this on PythonAnywhere to verify database setup.
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beyond_hunger.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from django.db import connection, OperationalError

def test_connection():
    """Test database connection."""
    try:
        print("Testing database connection...")
        connection.ensure_connection()
        print("✅ Database connection successful!")
        return True
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_users():
    """Check if users exist in the database."""
    try:
        user_count = User.objects.count()
        print(f"✅ Found {user_count} users in the database.")
        
        if user_count > 0:
            print("\nList of users:")
            for user in User.objects.all():
                print(f"- {user.username} (Staff: {user.is_staff}, Superuser: {user.is_superuser})")
        else:
            print("No users found. You may need to create a superuser.")
    except Exception as e:
        print(f"❌ Error querying users: {e}")

def main():
    """Run all database tests."""
    print("\n=== Database Connection Test ===\n")
    
    # Test database connection
    connection_ok = test_connection()
    
    if connection_ok:
        # Check users
        check_users()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 