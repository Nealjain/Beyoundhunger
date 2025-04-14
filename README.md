# Beyond Hunger

Beyond Hunger is a web application designed to facilitate food donations, manage a marketplace for food sharing, and collect monetary contributions to combat food waste and hunger.

## Features

- **Food Donation Management**: Users can donate excess food which volunteers can collect and distribute
- **Money Donation System**: Secure way to accept and track monetary contributions
- **Marketplace**: Platform for listing, selling, or giving away food items
- **User Authentication**: Email and social login (Google) support
- **Admin Dashboard**: Comprehensive tools for admins to manage users, donations, and marketplace listings
- **Email Notifications**: Automated emails for donation confirmations and marketplace interactions
- **Responsive Design**: Mobile-friendly interface for all users

## Tech Stack

- **Backend**: Django 5.1
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development), MySQL (production)
- **Authentication**: Django AllAuth with Google OAuth integration
- **Email**: SMTP integration with Gmail
- **Deployment**: PythonAnywhere

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/beyond-hunger.git
   cd beyond-hunger
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables (create a `.env` file):
   ```
   DJANGO_SECRET_KEY=your_secret_key
   DJANGO_DEBUG=True
   EMAIL_HOST_PASSWORD=your_email_app_password
   OPENAI_API_KEY=your_openai_api_key  # For chatbot functionality
   ```

5. Apply migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

## Google OAuth Setup

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. Configure the OAuth consent screen
3. Create OAuth credentials (Web application type)
4. Add authorized JavaScript origins:
   - `http://localhost:8000` (for development)
   - Your production domain (for production)
5. Add authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/` (for development)
   - Your production domain equivalent (for production)
6. Update settings with your credentials (use environment variables)

## Deployment Guide

### PythonAnywhere Deployment

1. Create a PythonAnywhere account
2. Upload your code:
   ```
   git clone https://github.com/yourusername/beyond-hunger.git
   ```
3. Create a virtual environment and install dependencies
4. Configure the WSGI file with environment variables
5. Set up static files
6. Configure your database
7. Set up a scheduled task for maintenance

## Project Structure

- `beyond_hunger/`: Project settings and root URL configuration
- `food_donation/`: Main application with models, views, and templates
- `templates/`: HTML templates for the website
- `static/`: CSS, JavaScript, and image files
- `media/`: User-uploaded content (images, etc.)

## Contributors

- Neal Jain - Developer

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Django documentation and community
- Bootstrap for the responsive design components
- PythonAnywhere for hosting services
