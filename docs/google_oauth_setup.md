# Setting Up Google OAuth for Beyond Hunger

This guide will walk you through the process of setting up Google OAuth for your Beyond Hunger application.

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page and select "New Project"
3. Enter a name for your project (e.g., "Beyond Hunger") and click "Create"
4. Wait for the project to be created and then select it from the project dropdown

## Step 2: Configure the OAuth Consent Screen

1. In the left sidebar, navigate to "APIs & Services" > "OAuth consent screen"
2. Select "External" as the user type and click "Create"
3. Fill in the required information:
   - App name: "Beyond Hunger"
   - User support email: Your email address
   - Developer contact information: Your email address
4. Click "Save and Continue"
5. On the "Scopes" page, click "Add or Remove Scopes" and add the following scopes:
   - `openid`
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
6. Click "Save and Continue"
7. On the "Test users" page, click "Add Users" and add your email address
8. Click "Save and Continue" and then "Back to Dashboard"

## Step 3: Create OAuth Client ID

1. In the left sidebar, navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" and select "OAuth client ID"
3. Select "Web application" as the application type
4. Enter a name for your client (e.g., "Beyond Hunger Web Client")
5. Add the following Authorized JavaScript origins:
   - `http://localhost:8000` (for development)
   - Your production domain (if applicable)
6. Add the following Authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/` (for development)
   - `http://127.0.0.1:8000/accounts/google/login/callback/` (for development)
   - Your production domain equivalents (if applicable)
7. Click "Create"
8. You will see a popup with your Client ID and Client Secret. Copy these values.

## Step 4: Configure Django Admin

1. Login to your Django admin at `/admin/`
2. Navigate to "Social Accounts" > "Social applications"
3. Click "Add social application":
   - Provider: Google
   - Name: Google
   - Client ID: Your Google Client ID
   - Secret key: Your Google Client Secret
   - Sites: Add your site from available sites
4. Click "Save"

## Step 5: Test the Integration

1. Start your Django development server:
   ```
   python manage.py runserver
   ```
2. Navigate to `http://localhost:8000/login/`
3. Click the "Sign in with Google" button
4. You should be redirected to Google's login page
5. After logging in, you should be redirected back to your application and be logged in

## Troubleshooting

If you encounter any issues:

1. Check that your Client ID and Client Secret are correctly entered in Django admin
2. Verify that your redirect URIs are correctly configured in the Google Cloud Console
3. Make sure you've added yourself as a test user in the OAuth consent screen
4. Check the Django logs for any error messages

## Production Considerations

For production deployment:

1. Add your production domain to the Authorized JavaScript origins and redirect URIs
2. Update your OAuth consent screen with your production information
3. Consider publishing your app if you want to allow all users to log in (not just test users)
4. Use environment variables for your Client ID and Client Secret instead of hardcoding them 