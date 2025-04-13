# Beyond Hunger - Food Donation Platform

A comprehensive platform for connecting food donors with volunteers to help eliminate hunger and reduce food waste. The platform facilitates food donations, volunteer management, and delivery coordination.

## Features

- **Food Donation Management**: Users can donate food items which are then assigned to volunteers for pickup and delivery
- **User Authentication**: Secure user registration and login system
- **Role-Based Access**: Support for donors, volunteers, and administrators
- **Donation Tracking**: Track the status of donations from initial submission to final delivery
- **Volunteer Management**: Manage volunteer profiles, availability, and assignments
- **Admin Dashboard**: Comprehensive dashboard for administrators to manage all aspects of the system
- **Monetary Donations**: Support for monetary contributions through UPI and bank transfers
- **REST API**: API endpoints for programmatic access to the platform's features
- **Mobile-Friendly**: Responsive design that works well on both desktop and mobile devices

## Tech Stack

- **Backend**: Django 5.1.7
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (for development), PostgreSQL (for production)
- **API**: Django REST Framework
- **Authentication**: Django's built-in authentication + Token authentication for API
- **Admin Interface**: Custom admin dashboard + Django admin

## Installation

### Prerequisites

- Python 3.12+
- pip
- virtualenv (optional but recommended)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/beyondhunger.git
   cd beyondhunger
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application:
   - Main site: http://127.0.0.1:8000/
   - Admin interface: http://127.0.0.1:8000/admin/

## Project Structure

```
beyondhunger/
├── beyond_hunger/        # Main project settings
├── food_donation/        # Main application code
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User-uploaded content
├── docs/                 # Documentation
├── utils/                # Utility scripts
└── manage.py             # Django management script
```

## Usage

1. **Making a donation**:
   - Register as a donor
   - Fill out the donation form with food details and pickup information
   
2. **Volunteering**:
   - Register as a volunteer
   - Update your availability and service area
   - Accept delivery assignments
   
3. **Administration**:
   - Use the admin dashboard to oversee all activities
   - Assign deliveries to volunteers
   - Track statistics and monitor system performance

## API Documentation

The Beyond Hunger API allows programmatic access to the platform's features. Authentication is required for most endpoints using token authentication.

### Key Endpoints

- `/api/login/`: Obtain authentication token
- `/api/statistics/`: Get system statistics
- `/api/donations/`: List or create donations
- `/api/volunteers/`: List volunteers
- `/api/assignments/`: List or manage delivery assignments

For detailed documentation, please refer to the [API Documentation](docs/api_documentation.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact:
- Email: contact@beyondhunger.org
- Website: https://beyondhunger.org
