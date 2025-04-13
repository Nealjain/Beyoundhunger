from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend that allows users to login using either username or email
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
            
        # Check if the input looks like an email address
        if '@' in username:
            # Try to fetch a user by email
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        else:
            # Try to fetch a user by username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
                
        # Check the password
        if user.check_password(password):
            return user
        return None 