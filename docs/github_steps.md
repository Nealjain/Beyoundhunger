# GitHub and Deployment Steps

## Pushing to GitHub

1. Create a new repository on GitHub at https://github.com/new
   - Name: beyond-hunger
   - Description: A platform connecting food donors with volunteers to reduce food waste and combat hunger
   - Set as Public
   - Do not initialize with README, .gitignore, or license (we already have these)

2. Connect your local repository to GitHub:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/beyond-hunger.git
   git branch -M main
   git push -u origin main
   ```

3. Verify your code is on GitHub by visiting your repository page

## Deploying to PythonAnywhere (Free Hosting)

Follow the detailed instructions in our [deployment.md](deployment.md) guide.

Key steps:
1. Create a free PythonAnywhere account
2. Set up a web app with manual configuration
3. Clone your GitHub repository
4. Set up virtual environment and install dependencies
5. Configure environment variables and static files
6. Apply migrations and collect static files
7. Reload your web app

## Alternative Free Hosting: Render

1. Create an account at https://render.com/
2. Connect your GitHub repository
3. Create a new Web Service
4. Select your repository
5. Configure the settings:
   - Name: beyond-hunger
   - Environment: Python
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn beyond_hunger.wsgi`
6. Add environment variables:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG` = False
   - `DJANGO_ALLOWED_HOSTS` = your-app-name.onrender.com
7. Deploy your application

## Making Updates

After making changes to your code:

1. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

2. Push to GitHub:
   ```bash
   git push
   ```

3. Update your deployment:
   - For PythonAnywhere: Follow the maintenance steps in deployment.md
   - For Render: Automatic deployments will occur when you push to GitHub 