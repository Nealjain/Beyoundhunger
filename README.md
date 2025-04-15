# Beyond Hunger

A web platform that facilitates food donation and community support, connecting those with excess food to those in need.

## Features

- **Food Donation System**: Easily donate excess food
- **Volunteer Management**: Sign up and coordinate volunteer efforts
- **Marketplace**: Share or request available food items
- **Bhandara Events**: Organize and participate in community food distribution events
- **Money Donations**: Securely contribute financial support
- **Admin Dashboard**: Comprehensive management interface

## Deployment

This project is configured for automatic deployment to PythonAnywhere using GitHub Actions.

### Setting Up GitHub Secrets

For the automatic deployment to work, you need to add these secrets to your GitHub repository:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `PA_USERNAME`: Your PythonAnywhere username
   - `PA_API_TOKEN`: Your PythonAnywhere API token
   - `PA_SSH_PASSWORD`: (Optional) Your PythonAnywhere account password for SSH access

### Getting Your PythonAnywhere API Token

1. Log in to PythonAnywhere
2. Go to Account → API token
3. Click "Create a new API token"
4. Copy the token and save it as a GitHub secret (PA_API_TOKEN)

### How Deployment Works

The GitHub Actions workflow:
1. Checks out your repository
2. Installs necessary Python dependencies
3. Verifies the API token
4. If SSH password is provided:
   - Pulls the latest code on PythonAnywhere
   - Runs migrations
   - Collects static files
5. Reloads your PythonAnywhere web app

For more details, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Local Development

### Prerequisites

- Python 3.12+
- pip
- virtualenv or venv

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Nealjain/Beyoundhunger.git
   cd Beyoundhunger
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Tech Stack

- **Backend**: Django 5.1
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development), MySQL (production)
- **Authentication**: Django AllAuth with Google OAuth integration
- **Email**: SMTP integration with Gmail

## Project Structure

- `beyond_hunger/`: Project settings and root URL configuration
- `food_donation/`: Main application with models, views, and templates
- `templates/`: HTML templates for the website
- `static/`: CSS, JavaScript, and image files
- `media/`: User-uploaded content (images, etc.)

## Contributors

- Neal Jain - Developer

## Acknowledgements

- Django documentation and community
- Bootstrap for the responsive design components
- PythonAnywhere for hosting services
