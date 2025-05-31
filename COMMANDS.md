# Quick Commands for Human Resources Django Project

## Environment Setup

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Database Operations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Development Server

```bash
# Start development server
python manage.py runserver

# Start with specific port
python manage.py runserver 8080
```

## Sample Data

```bash
# Create sample employee and department data
python manage.py shell -c "exec(open('create_sample_data.py').read())"

# Create sample performance data
python add_performance_data.py
```

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test employees

# Run specific test class
python manage.py test employees.tests.EmployeeModelTest
```

## API Endpoints (with authentication required)

### Authentication

- Login: http://127.0.0.1:8000/api-auth/login/
- Logout: http://127.0.0.1:8000/api-auth/logout/

### Main API

- API Root: http://127.0.0.1:8000/api/
- Employees: http://127.0.0.1:8000/api/employees/
- Departments: http://127.0.0.1:8000/api/departments/
- Performance Reviews: http://127.0.0.1:8000/api/performance-reviews/
- Performance Goals: http://127.0.0.1:8000/api/performance-goals/
- Performance Notes: http://127.0.0.1:8000/api/performance-notes/

### Special Endpoints

- Employee Statistics: http://127.0.0.1:8000/api/employees/statistics/
- Employees by Department: http://127.0.0.1:8000/api/employees/by_department/
- Employee Performance Reviews: http://127.0.0.1:8000/api/employees/{id}/performance-reviews/
- Employee Performance Goals: http://127.0.0.1:8000/api/employees/{id}/performance-goals/
- Employee Performance Notes: http://127.0.0.1:8000/api/employees/{id}/performance-notes/
- Overdue Goals: http://127.0.0.1:8000/api/performance-goals/overdue/
- Performance Statistics: http://127.0.0.1:8000/api/performance-reviews/statistics/

### Admin Interface

- Django Admin: http://127.0.0.1:8000/admin/

## Sample API Calls (using curl)

### Get all employees

```bash
curl -X GET http://127.0.0.1:8000/api/employees/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Search employees

```bash
curl -X GET "http://127.0.0.1:8000/api/employees/?search=john" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Filter by department

```bash
curl -X GET "http://127.0.0.1:8000/api/employees/?department=1" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Create new employee

```bash
curl -X POST http://127.0.0.1:8000/api/employees/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "employee_id": "EMP006",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@company.com",
    "position": "Software Engineer",
    "hire_date": "2025-06-01",
    "username": "janedoe",
    "password": "securepassword123"
  }'
```

## Production Deployment

### Environment Variables

Create `.env.production` with:

```
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/hr_db
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hr_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Security Checklist

```bash
python manage.py check --deploy
```
