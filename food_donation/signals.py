from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up, user_logged_in
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a UserProfile whenever a new User is created
    """
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'phone': '',
                'address': ''
            }
        )

@receiver(user_signed_up)
def user_signed_up_handler(request, user, **kwargs):
    """
    Handler for allauth's user_signed_up signal to ensure
    social auth users also get a UserProfile
    """
    userprofile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'phone': '',
            'address': ''
        }
    )
    
    # If this is a social account signup, mark the session for profile completion
    sociallogin = kwargs.get('sociallogin', None)
    if sociallogin:
        request.session['needs_profile_completion'] = True
        
        # If it's Google, try to get profile photo
        if sociallogin.account.provider == 'google' and 'picture' in sociallogin.account.extra_data:
            try:
                import requests
                from django.core.files.base import ContentFile
                
                # Get the profile picture URL
                picture_url = sociallogin.account.extra_data['picture']
                
                # Don't download immediately as we'll use the URL directly
                # Just store the social profile info and use the get_profile_photo_url method
                # to retrieve either uploaded photo or Google photo
            except Exception as e:
                print(f"Error getting Google profile picture: {str(e)}")

@receiver(user_logged_in)
def user_logged_in_handler(request, user, **kwargs):
    """
    Handler for allauth's user_logged_in signal to ensure
    social auth users have a UserProfile when they log in
    """
    try:
        userprofile = user.userprofile
        
        # If profile is incomplete (social login with empty address/phone), mark for completion
        if hasattr(request, 'session'):
            if kwargs.get('sociallogin', None) and (not userprofile.phone or not userprofile.address):
                request.session['needs_profile_completion'] = True
    except:
        UserProfile.objects.create(
            user=user,
            phone='',
            address=''
        )
        if hasattr(request, 'session'):
            request.session['needs_profile_completion'] = True 