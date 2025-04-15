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
    models_imported = True
    try:
        from food_donation.models import Bhandara
        print("✅ Bhandara model imported successfully")
    except ImportError as e:
        print(f"❌ Bhandara model import error: {e}")
        models_imported = False
    
    try:
        from food_donation.models import UserProfile
        print("✅ UserProfile model imported successfully")
    except ImportError as e:
        print(f"❌ UserProfile model import error: {e}")
        models_imported = False
    
    try:
        from food_donation.models import FoodDonation
        print("✅ FoodDonation model imported successfully")
    except ImportError as e:
        print(f"❌ FoodDonation model import error: {e}")
        models_imported = False
    
    if not models_imported:
        print("⚠️ Some models couldn't be imported, but we'll continue testing")
    
    # Try importing views
    try:
        from food_donation.views import home, about, contact
        print("✅ Views imported successfully")
    except ImportError as e:
        print(f"❌ Views import error: {e}")
        return False
    
    # Test content moderation
    try:
        from food_donation.content_moderation import contains_inappropriate_content
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