# SaaS Foundations Project

A production-ready Django SaaS boilerplate with authentication, subscriptions, and Razorpay integration.

## Features

- **Authentication**: User signup, login, password reset (allauth)
- **Subscriptions**: Custom plans and user subscriptions
- **Razorpay Integration**: Payment processing via Razorpay
- **API**: REST API with Django Rest Framework
- **Admin**: Django admin with admin user creation
- **Deployment**: Railway-ready with environment configuration

## Tech Stack

- **Framework**: Django 6.0.2
- **API**: Django Rest Framework
- **Database**: PostgreSQL (Neon DB)
- **Payments**: Razorpay
- **Authentication**: django-allauth

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd saas-foundations
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the `src` directory:
   ```env
   DJANGO_SECRET_KEY=your-secret-key
   DJANGO_DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   # For production:
   # DATABASE_URL=postgres://user:password@host:port/dbname
   
   # Razorpay configuration
   RAZORPAY_SECRET_KEY=your-key
   RAZORPAY_KEY_ID=your-key-id
   
   # Email configuration
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@example.com
   EMAIL_HOST_PASSWORD=your-email-password
   
   # Admin user
   ADMIN_USER_NAME=Admin user
   ADMIN_USER_EMAIL=admin@[EMAIL_ADDRESS]
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create admin user**
   ```bash
   python manage.py createadminuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Development

### Create a Superuser
```bash
python manage.py createadminuser
```

### Create Subscription Plans
Use the Django admin or the API to create subscription plans:
```bash
# Create plans via admin
python manage.py shell -c "from subscriptions.models import Subscription; Subscription.objects.create(name='Free', active=True, order=1)"

# Create API
curl -X POST http://localhost:8000/api/subscriptions/plans/ \
  -H "Authorization: Token your-auth-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "Pro", "active": true, "order": 2}'
```

### Test API
```bash
# Get subscription plans
curl http://localhost:8000/api/subscriptions/plans/

# Get current user (requires authentication)
curl http://localhost:8000/api/me/ \
  -H "Authorization: Token your-auth-token"

# Obtain token
curl -X POST http://localhost:8000/api/token/ \
  -d "username=your-username&password=your-password"
```

### Run Tests
```bash
python manage.py test
```

## Production

### Deployment on Railway
1. Push your code to GitHub
2. Import the project in Railway
3. Ensure environment variables are set correctly in Railway dashboard
4. Railway will automatically run migrations and collect static files

### Environment Variables
- `DJANGO_SECRET_KEY`: Production secret key
- `DATABASE_URL`: Production PostgreSQL connection string
- `RAZORPAY_KEY_ID`: Razorpay key id
- `RAZORPAY_SECRET_KEY`: Razorpay secret key
- `EMAIL_*`: Production email configuration

## Project Structure

```
src/
├── customers/       # Customer management
├── subscriptions/   # Plans and subscriptions
├── checkouts/       # Payment processing
├── profiles/        # User profiles
├── commando/        # Management commands
├── myproject/       # Project settings and URLs
│   ├── settings.py  # Main settings
│   └── api_urls.py  # API URL patterns
├── templates/       # HTML templates
├── static/          # Static files
├── media/           # User-uploaded media
└── manage.py        # Django management script
```

## Author

- **Bhuvan Goel** - [bhuvangoel04](https://github.com/bhuvangoel04)

## License

MIT