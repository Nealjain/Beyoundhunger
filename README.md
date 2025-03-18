# Beyond Hunger

Beyond Hunger is a web application that connects food donors with volunteers who can deliver surplus food to those in need. The platform helps reduce food waste and combats hunger by creating a sustainable food ecosystem.

## Live Demo

Check out our live demo at: https://nealjain.pythonanywhere.com/

## Features

- **Food Donation Management**: Allow restaurants, catering services, and individuals to donate surplus food
- **Volunteer Coordination**: Connect volunteers with food donation pickups and deliveries
- **User Profiles**: Separate interfaces for donors and volunteers
- **Real-time Status Updates**: Track donations from submission to delivery
- **Admin Dashboard**: Comprehensive admin interface for managing donations and volunteers
- **Responsive Design**: Mobile-friendly interface accessible on any device
- **Automated Deployment**: Changes are automatically deployed to PythonAnywhere

## Technology Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite (development), PostgreSQL (production optional)
- **Authentication**: Django Authentication System
- **Deployment**: Automatic deployment to PythonAnywhere via GitHub Actions
- **Continuous Integration**: GitHub Actions workflow for testing and deployment

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Nealjain/Beyoundhunger.git
   cd Beyoundhunger
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file with your configuration settings

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

8. Visit `http://127.0.0.1:8000/` in your browser

## Deployment

### PythonAnywhere (Recommended for Free Hosting)

1. Sign up for a free PythonAnywhere account at https://www.pythonanywhere.com/
2. Create a new web app with manual configuration using Python 3.12
3. Set up a virtual environment and install dependencies
4. Configure WSGI file to point to your Django project
5. Add environment variables in the PythonAnywhere dashboard
6. Set up static files in the web app configuration

Detailed deployment instructions are available in the [deployment guide](deployment.md).

### Alternative Deployment Options

The application can also be deployed on:
- Render
- Heroku
- DigitalOcean App Platform
- AWS Elastic Beanstalk

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Team

- Neal Jain - Founder & CEO
- Shreyasi - Co-founder & COO
- Manali - Co-founder & CTO

## Contact

If you have any questions or suggestions, please open an issue or contact us at example@beyondhunger.com.
