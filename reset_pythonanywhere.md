# Reset and Redeploy on PythonAnywhere

Follow these steps to completely reset and redeploy your application on PythonAnywhere:

## 1. Delete Existing Files

1. Log in to your PythonAnywhere account at https://www.pythonanywhere.com/
2. Open a Bash console from your dashboard
3. Run these commands to delete the existing project:

```bash
rm -rf ~/beyondhunger
rm -rf ~/beyondhunger_old
```

## 2. Clone Fresh Repository

```bash
git clone https://github.com/Nealjain/Beyoundhunger.git ~/beyondhunger
cd ~/beyondhunger
```

## 3. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure WSGI File

1. Go to the Web tab in your PythonAnywhere dashboard
2. Click on the WSGI configuration file link
3. Replace the entire content with the code from your `wsgi_for_pythonanywhere.py` file
4. Make sure the path is correct: `/home/nealjain/beyondhunger`
5. Save the file

## 5. Configure Static Files

1. In the Web tab, under "Static files":
2. Add these mappings:
   - URL: `/static/` → Directory: `/home/nealjain/beyondhunger/staticfiles`
   - URL: `/media/` → Directory: `/home/nealjain/beyondhunger/media`

## 6. Initialize Database and Collect Static Files

```bash
cd ~/beyondhunger
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # Create an admin user if needed
```

## 7. Fix User Profiles (If Needed)

```bash
cd ~/beyondhunger
source venv/bin/activate
python manage.py create_user_profile
```

## 8. Reload Web App

1. Go back to the Web tab
2. Click the "Reload" button for your web app

## 9. Check Error Logs

If you still encounter issues, check:
1. Error log in the Web tab
2. Access log in the Web tab

## Troubleshooting Tips

1. Make sure all paths in the WSGI file match your actual directory structure
2. Verify that your `DEBUG` setting is `False` in production
3. Check that all required environment variables are set
4. Ensure database migrations are applied correctly
5. Verify static files are collected and properly configured 