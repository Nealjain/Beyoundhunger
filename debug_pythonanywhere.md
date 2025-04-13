# Debugging PythonAnywhere Deployment

If your site is redirecting to the login page or not loading properly, follow these steps to debug the issues.

## 1. Check Error Logs

The most important step is to check the error logs:

1. Go to the Web tab in PythonAnywhere
2. Scroll down to the "Logs" section
3. Click on "Error log" and examine the most recent errors

Common errors and solutions:

### ImportError or ModuleNotFoundError
- **Problem**: Missing Python package
- **Solution**: Install the missing package with `pip install package_name`

### PermissionError
- **Problem**: File permissions issues
- **Solution**: Run `chmod -R u+rwX ~/beyondhunger` to fix permissions

### Database errors
- **Problem**: Migration issues or incorrect DB settings
- **Solution**: Run migrations again or check DB configuration

## 2. Fix WSGI File

Make sure your WSGI file has the correct:
- Path to your project directory
- Environment variables set properly
- Debug mode set to False
- Proper allowed hosts

```python
# Example of a correct WSGI file for PythonAnywhere
import os
import sys

path = '/home/nealjain/beyondhunger'  # Verify this path exists!
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'
os.environ['DJANGO_SECRET_KEY'] = 'your-secret-key-here'  # Set your secure key
os.environ['DJANGO_DEBUG'] = 'False'  # Production mode
os.environ['DJANGO_ALLOWED_HOSTS'] = 'nealjain.pythonanywhere.com,localhost,127.0.0.1'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 3. Verify Directory Structure

Make sure your files are in the expected locations:
```bash
cd ~
ls -la  # Check home directory
ls -la beyondhunger/  # Check project directory
```

## 4. Test Database Connection

Run these commands in a Bash console:
```bash
cd ~/beyondhunger
source venv/bin/activate
python manage.py shell
```

In the shell:
```python
from django.db import connection
connection.ensure_connection()  # Should not raise errors
exit()
```

## 5. Try Debug Mode Temporarily

Modify your WSGI file to set Debug mode True temporarily:
```python
os.environ['DJANGO_DEBUG'] = 'True'  # TEMPORARILY for troubleshooting
```

Reload the web app and check for detailed error messages.

## 6. Check Static Files Configuration

Verify your static files configuration in the Web tab:
- URL: `/static/` → Directory: `/home/nealjain/beyondhunger/staticfiles`
- URL: `/media/` → Directory: `/home/nealjain/beyondhunger/media`

## 7. Complete Reset Option

If all else fails, perform a complete reset:
```bash
cd ~
rm -rf beyondhunger
git clone https://github.com/Nealjain/Beyoundhunger.git beyondhunger
cd beyondhunger
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./build.sh
```

After reset, go to Web tab and:
1. Update the WSGI file
2. Verify static files paths
3. Reload the web app 