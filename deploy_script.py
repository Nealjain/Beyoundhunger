#!/usr/bin/env python3
"""
Deploy script for PythonAnywhere
Verifies API token and reloads the web app
"""
import os
import requests
import sys
import time
import logging

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

def deploy():
    """Deploy the web app to PythonAnywhere by reloading it"""
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
                logger.info('✓ Deployment successful!')
                return True
            else:
                logger.error(f'✗ Deployment attempt {attempt} failed with status code {response.status_code}')
                logger.error(f'Response: {response.text}')
                
                if attempt < max_attempts:
                    wait_time = attempt * 5
                    logger.info(f'Retrying in {wait_time} seconds...')
                    time.sleep(wait_time)
                else:
                    logger.error('All retry attempts failed')
                    return False
                    
        except requests.exceptions.Timeout:
            logger.error(f'✗ Request timed out during deployment attempt {attempt}')
            if attempt < max_attempts:
                wait_time = attempt * 5
                logger.info(f'Retrying in {wait_time} seconds...')
                time.sleep(wait_time)
            else:
                logger.error('All retry attempts failed')
                return False
        except Exception as e:
            logger.error(f'✗ Error during deployment attempt {attempt}: {str(e)}')
            if attempt < max_attempts:
                wait_time = attempt * 5
                logger.info(f'Retrying in {wait_time} seconds...')
                time.sleep(wait_time)
            else:
                logger.error('All retry attempts failed')
                return False
    
    return False

if __name__ == "__main__":
    logger.info('Starting PythonAnywhere deployment')
    success = deploy()
    if not success:
        logger.error('Deployment failed!')
        sys.exit(1)
    logger.info('Deployment completed successfully')
    sys.exit(0) 