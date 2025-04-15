# PythonAnywhere Deployment Checklist

## Before Deployment
- [ ] Make sure all changes are committed to GitHub repository
- [ ] Generate a secure SECRET_KEY using the provided script
- [ ] Make sure requirements.txt contains all necessary packages
- [ ] Ensure all media and static files are properly organized

## PythonAnywhere Account Setup
- [ ] Create a PythonAnywhere account at https://www.pythonanywhere.com/
- [ ] Verify your email address
- [ ] Choose a meaningful username (will be part of your site's URL)

## Deployment Steps (Follow deploy_to_pythonanywhere.md)
- [ ] Create a new web app on PythonAnywhere
- [ ] Clone your GitHub repository
- [ ] Set up a virtual environment
- [ ] Configure the WSGI file with your settings
- [ ] Set up static files mapping
- [ ] Configure your virtual environment path
- [ ] Run database migrations
- [ ] Create a superuser account
- [ ] Collect static files
- [ ] Reload the web app

## Post-Deployment
- [ ] Visit your site at https://yourusername.pythonanywhere.com/
- [ ] Test user authentication (login, registration)
- [ ] Test the donation process
- [ ] Test volunteer assignments
- [ ] Test the marketplace features
- [ ] Check mobile responsiveness
- [ ] Verify that the chat feature works

## Important Notes
1. **SECRET_KEY:** Use the generated SECRET_KEY value from running `generate_secret_key.py`:
   ```
   &$2)$b)ll4&bhp#f1cqetl9=0s)p5^sli$oo4#3zldjvtyh)lf
   ```

2. **Database:** PythonAnywhere will use SQLite by default, which is fine for a first project. For larger projects, consider using their MySQL option.

3. **Debug Mode:** Make sure DEBUG is set to False in production (handled in the WSGI configuration).

4. **CORS Settings:** The deployment setup handles CORS configuration for your domain.

5. **HTTPS:** PythonAnywhere provides HTTPS on their domain automatically. 