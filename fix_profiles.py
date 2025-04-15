#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beyond_hunger.settings")
django.setup()

# Import models
from food_donation.models import UserProfile
from django.contrib.auth.models import User

print("Starting user profile check...")

# Create profiles for users that don't have one
for user in User.objects.all():
    try:
        profile = user.userprofile
        print(f"User {user.username} already has a profile")
    except:
        print(f"Creating profile for {user.username}")
        profile = UserProfile(user=user, is_donor=True)
        profile.save()

print("\\nAll users should now have profiles. Checking...")

# Verify all users have profiles
missing_profiles = []
for user in User.objects.all():
    try:
        profile = user.userprofile
    except:
        missing_profiles.append(user.username)

if missing_profiles:
    print(f"Warning: Users still missing profiles: {', '.join(missing_profiles)}")
else:
    print("Success! All users now have profiles.")

# Display all users and their profiles for verification
print("\\nUser profile information:")
for user in User.objects.all():
    try:
        profile = user.userprofile
        print(f"User: {user.username}, Email: {user.email}, Is donor: {profile.is_donor}, Is volunteer: {profile.is_volunteer}")
    except Exception as e:
        print(f"User: {user.username}, Error: {e}") 