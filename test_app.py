#!/usr/bin/env python3
"""
Test script to verify the application runs correctly.
"""

import os
import sys
import django
from django.core.management import call_command

def run_tests():
    print("Testing BeyondHunger application...")
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beyond_hunger.settings')
    django.setup()
    
    # Try importing key modules
    try:
        from food_donation.models import Bhandara, UserProfile, FoodDonation
        from food_donation.views import home, about, contact
        from food_donation.content_moderation import contains_inappropriate_content
        
        print("✅ All modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test content moderation
    try:
        result = contains_inappropriate_content("This is a normal text")
        if result is False:
            print("✅ Content moderation working correctly")
        else:
            print("❌ Content moderation not working as expected")
            return False
    except Exception as e:
        print(f"❌ Content moderation error: {e}")
        return False
    
    # Try checking migrations
    try:
        call_command('showmigrations', 'food_donation')
        print("✅ Migrations are available")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
    
    print("\nApplication tests completed successfully! ✅")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 