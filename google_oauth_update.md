# Updating Google OAuth Redirect URIs

Follow these steps to update your Google OAuth redirect URIs in the Google Cloud Console:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project from the dropdown at the top
3. In the left sidebar, navigate to "APIs & Services" > "Credentials"
4. Find your OAuth 2.0 Client ID and click on it to edit
5. Under "Authorized redirect URIs", add the following URIs:
   ```
   http://127.0.0.1:8000/social-auth/complete/google-oauth2/
   http://localhost:8000/social-auth/complete/google-oauth2/
   ```
6. Click "Save" to update your settings

## Important Notes

- Make sure you're using the exact URLs as shown above, including the trailing slash
- The domain (127.0.0.1 or localhost) must match what you're using in your browser
- After updating, it may take a few minutes for the changes to propagate

## Testing

After updating the redirect URIs:

1. Restart your Django server
2. Clear your browser cookies for the Google login domain
3. Try logging in with Google again

If you're still experiencing issues, check the Django server logs for more detailed error messages. 