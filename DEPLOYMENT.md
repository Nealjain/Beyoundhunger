# Deploying to PythonAnywhere

This guide explains how to deploy the Beyond Hunger application to PythonAnywhere using GitHub Actions.

## Initial Setup on PythonAnywhere

1. Create a PythonAnywhere account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Go to the "Web" tab and create a new web app
   - Choose "Manual configuration"
   - Select the latest Python version (3.9+)
3. Set up the virtual environment:
   ```bash
   mkvirtualenv --python=python3.9 myenv
   pip install -r requirements.txt
   ```
4. Configure your web app:
   - Set the source code directory to your project path
   - Configure the WSGI file to point to your Django application
   - Set up static files mapping

## GitHub Actions Setup

The repository is configured to automatically deploy to PythonAnywhere whenever changes are pushed to the main branch.

### Required Secrets

You need to set up the following secrets in your GitHub repository:

1. Go to your GitHub repository
2. Navigate to Settings -> Secrets and variables -> Actions
3. Add the following secrets:
   - `PA_USERNAME`: Your PythonAnywhere username (e.g., beyoundhunger12)
   - `PA_API_TOKEN`: Your PythonAnywhere API token
   - `PA_SSH_PASSWORD`: (Optional) Your PythonAnywhere account password for SSH access

### Getting Your PythonAnywhere API Token

1. Log in to PythonAnywhere
2. Go to Account -> API token
3. Click "Create a new API token"
4. Copy the token and save it as a GitHub secret (PA_API_TOKEN)

## How the Deployment Works

The GitHub Actions workflow does the following:

1. Checks out your repository
2. Installs the necessary Python dependencies
3. Verifies the API token is valid
4. Uses SSH to connect to PythonAnywhere and:
   - Pulls the latest code from your repository
   - Runs migrations
   - Collects static files
5. Reloads your PythonAnywhere web app using the API

## Manual Deployment

If you need to deploy manually:

1. SSH into PythonAnywhere
2. Navigate to your project directory
3. Pull the latest code:
   ```bash
   git pull origin main
   ```
4. Activate your virtual environment:
   ```bash
   workon myenv
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```
7. Reload your web app from the PythonAnywhere web interface

## Troubleshooting

If the automatic deployment fails:

1. Check the GitHub Actions logs for errors
2. Verify that your API token is correct and has not expired
3. Make sure your repository is properly set up on PythonAnywhere
4. Try deploying manually to see if there are any issues with your application

### Common Issues

- **Invalid API token**: Make sure you've created a valid token and stored it as `PA_API_TOKEN` in your GitHub secrets
- **Incorrect username**: Verify your PythonAnywhere username is stored correctly as `PA_USERNAME` in GitHub secrets
- **SSH connection failures**: If you're using SSH for code sync, ensure your password is correct in the `PA_SSH_PASSWORD` secret

For more help, refer to the [PythonAnywhere documentation](https://help.pythonanywhere.com/pages/). 