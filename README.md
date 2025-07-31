# Django Project Template

A production-ready Django project template with comprehensive authentication and user management system, built with Django REST Framework and JWT authentication.

## Features

### 🔐 Authentication & User Management
- **JWT Authentication** with access and refresh tokens
- **Email-based authentication** (no username required)
- **Email verification** with secure tokens
- **Password reset** functionality with rate limiting
- **Password change** for authenticated users
- **User profile management** with comprehensive fields


### 📧 Email System
- **Welcome emails** for new users
- **Email verification** emails
- **Password reset** emails
- **Password sharing** emails
- **HTML email templates** with responsive design
- **Email integration** for reliable email delivery

### 🛡️ Security Features
- **Password validation** with multiple requirements
- **Rate limiting** on sensitive endpoints
- **XSS prevention** middleware
- **Token expiration** and validation
- **Secure password hashing**
- **Email normalization** and validation

### 🧪 Testing
- **Comprehensive test suite** with pytest
- **Factory Boy** for test data generation
- **Test helpers** and utilities
- **Email mocking** for tests
- **Custom test fixtures**

## Project Structure

```
django-project-template/
├── app/
│   ├── accounts/                 # User authentication app
│   │   ├── admin.py             # Admin configuration
│   │   ├── apps.py              # App configuration
│   │   ├── emails.py            # Email classes
│   │   ├── models.py            # User model
│   │   ├── permissions.py       # Custom permissions
│   │   ├── serializers/         # API serializers
│   │   ├── tests/               # Test suite
│   │   ├── throttles.py         # Rate limiting
│   │   ├── urls.py              # URL routing
│   │   └── views.py             # API views
│   ├── config/                  # Project configuration
│   │   ├── settings/            # Settings files
│   │   ├── urls.py              # Main URL configuration
│   │   └── v1/                  # API versioning
│   ├── core/                    # Core models and utilities
│   │   ├── choices/             # Choice fields
│   │   └── models/              # Base models
│   ├── templates/               # Email templates
│   └── utils/                   # Utility functions
│       ├── exceptions.py        # Custom exceptions
│       ├── factories/           # Test factories
│       ├── helpers.py           # Test helpers
│       ├── validators.py        # Field validators
│       └── views.py             # Base viewsets
├── conftest.py                  # Pytest configuration
├── pytest.ini                  # Pytest settings
├── requirements.txt             # Dependencies
└── README.md                   # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (recommended) or SQLite
- Virtual environment

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-project-template
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/v1/accounts/auth/login/` - User login
- `GET /api/v1/accounts/auth/logout/` - User logout
- `POST /api/v1/accounts/signup/` - User registration

### Email Verification
- `POST /api/v1/accounts/verifications/email/` - Verify email
- `POST /api/v1/accounts/verifications/resend-email-token/` - Resend verification

### Password Management
- `POST /api/v1/accounts/auth/password/request-token/` - Request password reset
- `GET /api/v1/accounts/auth/password/{token}/reset/` - Validate reset token
- `POST /api/v1/accounts/auth/password/{token}/reset/` - Reset password
- `POST /api/v1/accounts/auth/change-password/` - Change password

### User Profile
- `GET /api/v1/accounts/profile/` - Get user profile
- `PUT /api/v1/accounts/profile/` - Update user profile

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME=5
JWT_REFRESH_TOKEN_LIFETIME=1
```

### Settings

The project uses multiple settings files:
- `config/settings/base.py` - Base settings
- `config/settings/develop.py` - Development settings
- `config/settings/production.py` - Production settings
- `config/settings/test.py` - Test settings

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest accounts/tests/test_account_api.py

# Run with coverage
pytest --cov=accounts --cov-report=html

# Run with verbose output
pytest -v
```

### Test Structure
- **Unit tests** for models and utilities
- **Integration tests** for API endpoints
- **Email tests** with mocked email sending
- **Authentication tests** with JWT tokens

## User Model

The custom User model includes:

### Fields
- `email` - Primary identifier (unique)
- `first_name`, `last_name` - User names
- `gender` - Gender choice field
- `address`, `state`, `country` - Location fields
- `is_email_verified` - Email verification status
- `email_verification_token` - Email verification token
- `forgot_password_token` - Password reset token


### Methods
- `send_verification_email()` - Send email verification
- `verify_email()` - Verify email with token
- `generate_forgot_password_reset_token()` - Generate reset token
- `reset_password()` - Reset password with token
- `change_password()` - Change password for authenticated users

## Email Templates

The project includes responsive HTML email templates:

- `templates/emails/accounts/welcomeEmail.html` - Welcome email
- `templates/emails/accounts/emailVerification.html` - Email verification
- `templates/emails/accounts/password_reset.html` - Password reset
- `templates/emails/accounts/share_password.html` - Password sharing

## Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### Rate Limiting
- Password reset requests: 1 per 3 minutes per email
- Login attempts: Configurable limits
- API endpoints: Customizable throttling

### Token Security
- JWT tokens with configurable expiration
- Secure token generation and validation
- Token blacklisting on logout

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up email service (SendGrid)
- [ ] Configure static file serving
- [ ] Set up SSL/HTTPS
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure backup strategy

### Docker Support
```bash
# Build image
docker build -t django-project .

# Run container
docker run -p 8000:8000 django-project
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test examples

## Acknowledgments

- Django REST Framework for the excellent API framework
- Simple JWT for JWT authentication
- Factory Boy for test data generation
- SendGrid for email delivery
- All contributors to the open-source packages used 