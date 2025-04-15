# Google OAuth Redirect URI Fix Instructions

To fix the 'redirect_uri_mismatch' error when signing in with Google, follow these steps:

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Select your project
3. Navigate to 'APIs & Services' > 'Credentials'
4. Find and edit your OAuth 2.0 Client ID
5. Under 'Authorized redirect URIs', add these exact URIs:

```
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
https://beyondhunger.pythonanywhere.com/accounts/google/login/callback/
```

6. Click 'Save'
7. Wait a few minutes for changes to propagate
8. Try logging in again

## Why this error occurs

The error message:
```
Error 400: redirect_uri_mismatch
```

This occurs because Django AllAuth is trying to redirect to `/accounts/google/login/callback/`, but your Google OAuth configuration doesn't have this exact path authorized.

## Common mistakes to avoid:

1. Missing trailing slash at the end of the URI
2. Using the wrong domain (make sure it matches what you use in your browser)
3. Typographical errors in the URL
4. Not waiting for Google to propagate the changes

If the issue persists after following these steps, check your Django AllAuth configuration in settings.py to ensure it matches the OAuth client ID and secret you're using in Google Cloud Console. 