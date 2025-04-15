#!/usr/bin/env python3
"""
Deploy script for PythonAnywhere
Handles SSH code synchronization and web app reload
"""
import os
import sys
import requests
import time
import logging

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('deploy')

def verify_api_token():
    """Verify that the API token is valid by making a request to the PythonAnywhere API"""
    username = os.environ.get('PA_USERNAME')
    token = os.environ.get('PA_API_TOKEN')
    
    if not username or not token:
        logger.error('Error: Environment variables PA_USERNAME and PA_API_TOKEN must be set')
        sys.exit(1)
    
    logger.info(f'Verifying API token for {username}...')
    try:
        cpu_response = requests.get(
            f'https://www.pythonanywhere.com/api/v0/user/{username}/cpu/',
            headers={'Authorization': f'Token {token}'},
            timeout=30  # Add timeout to prevent hanging
        )
        if cpu_response.status_code == 200:
            logger.info('✓ API token valid')
            return True
        else:
            logger.error(f'✗ API token validation failed with status code {cpu_response.status_code}')
            logger.error(f'Response: {cpu_response.content.decode()}')
            return False
    except requests.exceptions.Timeout:
        logger.error('✗ API request timed out during token verification')
        return False
    except requests.exceptions.ConnectionError:
        logger.error('✗ Connection error during token verification')
        return False
    except Exception as e:
        logger.error(f'✗ Error validating API token: {str(e)}')
        return False

def sync_code_via_ssh():
    """Synchronize code via SSH if credentials are available"""
    if not PARAMIKO_AVAILABLE:
        logger.warning("Paramiko not available - skipping SSH code sync")
        return True
    
    username = os.environ.get('PA_USERNAME')
    password = os.environ.get('PA_SSH_PASSWORD')
    
    if not password:
        logger.info("SSH password not provided - skipping code sync")
        return True
    
    try:
        logger.info(f'Connecting to {username}.pythonanywhere.com via SSH...')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=f'{username}.pythonanywhere.com',
            username=username,
            password=password,
            timeout=30
        )
        
        # Execute git pull
        logger.info('Pulling latest code from repository...')
        stdin, stdout, stderr = client.exec_command('cd ~/beyoundhunger && git pull')
        stdout_data = stdout.read().decode()
        stderr_data = stderr.read().decode()
        logger.info(f'Pull output: {stdout_data}')
        if stderr_data:
            logger.warning(f'Pull errors: {stderr_data}')
        
        # Run migrations
        logger.info('Running migrations...')
        stdin, stdout, stderr = client.exec_command('cd ~/beyoundhunger && python manage.py migrate')
        stdout_data = stdout.read().decode()
        stderr_data = stderr.read().decode()
        logger.info(f'Migration output: {stdout_data}')
        if stderr_data:
            logger.warning(f'Migration errors: {stderr_data}')
        
        # Collect static files
        logger.info('Collecting static files...')
        stdin, stdout, stderr = client.exec_command('cd ~/beyoundhunger && python manage.py collectstatic --noinput')
        stdout_data = stdout.read().decode()
        stderr_data = stderr.read().decode()
        logger.info(f'Collectstatic output: {stdout_data}')
        if stderr_data:
            logger.warning(f'Collectstatic errors: {stderr_data}')
        
        client.close()
        logger.info('✓ SSH operations completed successfully')
        return True
    except Exception as e:
        logger.error(f'✗ Error during SSH operations: {str(e)}')
        logger.warning('Continuing with webapp reload despite SSH errors')
        return False

def reload_webapp():
    """Reload the PythonAnywhere web app using the API"""
    username = os.environ.get('PA_USERNAME')
    token = os.environ.get('PA_API_TOKEN')
    
    if not verify_api_token():
        logger.error('Failed to verify API token, aborting deployment')
        sys.exit(1)
    
    logger.info('Reloading PythonAnywhere Web App...')
    reload_url = f'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{username}.pythonanywhere.com/reload/'
    
    # Add retry logic
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f'Attempt {attempt} of {max_attempts}')
            response = requests.post(
                reload_url,
                headers={'Authorization': f'Token {token}'},
                timeout=60  # Longer timeout for reload operation
            )
            
            if response.status_code == 200:
                logger.info('✓ Web app reload successful!')
                return True
            else:
                logger.error(f'✗ Reload attempt {attempt} failed with status code {response.status_code}')
                logger.error(f'Response: {response.text}')
                
                if attempt < max_attempts:
                    wait_time = attempt * 5
                    logger.info(f'Retrying in {wait_time} seconds...')
                    time.sleep(wait_time)
                else:
                    logger.error('All retry attempts failed')
                    return False
                    
        except requests.exceptions.Timeout:
            logger.error(f'✗ Request timed out during reload attempt {attempt}')
            if attempt < max_attempts:
                wait_time = attempt * 5
                logger.info(f'Retrying in {wait_time} seconds...')
                time.sleep(wait_time)
            else:
                logger.error('All retry attempts failed')
                return False
        except Exception as e:
            logger.error(f'✗ Error during reload attempt {attempt}: {str(e)}')
            if attempt < max_attempts:
                wait_time = attempt * 5
                logger.info(f'Retrying in {wait_time} seconds...')
                time.sleep(wait_time)
            else:
                logger.error('All retry attempts failed')
                return False
    
    return False

def deploy():
    """Main deployment function - handles both SSH sync and web app reload"""
    logger.info('Starting PythonAnywhere deployment')
    
    # First sync code via SSH if possible
    sync_code_via_ssh()
    
    # Then reload the web app
    success = reload_webapp()
    
    if not success:
        logger.error('Deployment failed!')
        sys.exit(1)
    logger.info('Deployment completed successfully')
    return True

if __name__ == "__main__":
    deploy()
    sys.exit(0) 