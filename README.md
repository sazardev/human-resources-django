# Human Resources Management System

A Django REST Framework application for managing human resources, including employee records, departments, and organizational data.

## Features

- **Employee Management**: Complete CRUD operations for employee records
- **Department Organization**: Manage company departments and employee assignments
- **Performance Tracking**: Comprehensive performance management system
  - Performance Reviews with detailed ratings and feedback
  - Performance Goals with progress tracking
  - Performance Notes for observations and achievements
- **REST API**: Full REST API with Django REST Framework
- **Admin Interface**: Django admin for easy data management
- **Environment Configuration**: Separate settings for development and production
- **Database Support**: SQLite for development, PostgreSQL for production
- **API Documentation**: Browsable API with Django REST Framework

## Technology Stack

- **Backend**: Django 5.2.1
- **API**: Django REST Framework 3.16.0
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Environment Management**: python-dotenv
- **Filtering**: django-filter
- **Authentication**: Django built-in + Token authentication

## Quick Start

### Prerequisites

- Python 3.8+
- Git

### Installation

1. **Clone the repository** (if using git):

   ```bash
   git clone <repository-url>
   cd human-resources
   ```

2. **Create and activate virtual environment**:

   ```bash
   python -m venv venv

   # On Windows
   .\venv\Scripts\Activate.ps1

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:

   - Copy `.env.example` to `.env` (if available) or create `.env` file
   - Update environment variables as needed:
     ```
     DEBUG=True
     SECRET_KEY=your-secret-key-here
     DATABASE_URL=sqlite:///db.sqlite3
     ```

5. **Database Setup**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**:

   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server**:

   ```bash
   python manage.py runserver
   ```

8. **Access the Application**:
   - API Root: http://127.0.0.1:8000/api/
   - Admin Interface: http://127.0.0.1:8000/admin/
   - API Documentation: http://127.0.0.1:8000/api/ (browsable API)

## API Endpoints

### Authentication

- `POST /api-auth/login/` - Login
- `POST /api-auth/logout/` - Logout

### Employees

- `GET /api/employees/` - List all employees
- `POST /api/employees/` - Create new employee
- `GET /api/employees/{id}/` - Get employee details
- `PUT /api/employees/{id}/` - Update employee
- `DELETE /api/employees/{id}/` - Delete employee
- `POST /api/employees/{id}/change_status/` - Change employee status
- `GET /api/employees/by_department/` - Filter employees by department
- `GET /api/employees/statistics/` - Get employee statistics

### Departments

- `GET /api/departments/` - List all departments
- `POST /api/departments/` - Create new department
- `GET /api/departments/{id}/` - Get department details
- `PUT /api/departments/{id}/` - Update department
- `DELETE /api/departments/{id}/` - Delete department

### Performance Reviews

- `GET /api/performance-reviews/` - List all performance reviews
- `POST /api/performance-reviews/` - Create new performance review
- `GET /api/performance-reviews/{id}/` - Get performance review details
- `PUT /api/performance-reviews/{id}/` - Update performance review
- `DELETE /api/performance-reviews/{id}/` - Delete performance review
- `GET /api/performance-reviews/statistics/` - Get review statistics
- `GET /api/employees/{id}/performance-reviews/` - Get employee's reviews

### Performance Goals

- `GET /api/performance-goals/` - List all performance goals
- `POST /api/performance-goals/` - Create new performance goal
- `GET /api/performance-goals/{id}/` - Get performance goal details
- `PUT /api/performance-goals/{id}/` - Update performance goal
- `DELETE /api/performance-goals/{id}/` - Delete performance goal
- `POST /api/performance-goals/{id}/update_progress/` - Update goal progress
- `GET /api/performance-goals/overdue/` - Get overdue goals
- `GET /api/employees/{id}/performance-goals/` - Get employee's goals

### Performance Notes

- `GET /api/performance-notes/` - List all performance notes
- `POST /api/performance-notes/` - Create new performance note
- `GET /api/performance-notes/{id}/` - Get performance note details
- `PUT /api/performance-notes/{id}/` - Update performance note
- `DELETE /api/performance-notes/{id}/` - Delete performance note
- `GET /api/employees/{id}/performance-notes/` - Get employee's notes

## API Features

### Filtering

- Filter employees by department, employment status, position
- Search employees by name, email, employee ID, position
- Order results by various fields

### Pagination

- Default page size: 20 items
- Use `?page=N` parameter for navigation

### Example API Usage

```bash
# Get all employees
curl -X GET http://127.0.0.1:8000/api/employees/

# Search employees
curl -X GET "http://127.0.0.1:8000/api/employees/?search=john"

# Filter by department
curl -X GET "http://127.0.0.1:8000/api/employees/?department=1"

# Create new employee
curl -X POST http://127.0.0.1:8000/api/employees/ \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@company.com",
    "position": "Software Developer",
    "hire_date": "2025-01-01",
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

## Environment Configuration

### Development (.env)

```
DEBUG=True
SECRET_KEY=your-development-secret-key
DATABASE_URL=sqlite:///db.sqlite3
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### Production (.env.production)

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
```

## Models

### Employee Model

- Personal information (name, email, phone)
- Employment details (ID, department, position, status, salary)
- Address information
- Performance tracking properties
- Timestamps

### Department Model

- Name and description
- Timestamps

### Performance Models

#### PerformanceReview Model

- Employee and reviewer information
- Review type and period
- Detailed ratings (technical skills, communication, teamwork, etc.)
- Feedback and recommendations
- Status tracking

#### PerformanceGoal Model

- Goal information and categorization
- Timeline and progress tracking
- Success criteria and outcomes
- Status management with automatic updates

#### PerformanceNote Model

- Observations and achievements
- Note types (achievement, feedback, coaching, etc.)
- Privacy controls
- Associations with goals and reviews

## Development

### Project Structure

```
human-resources/
├── human_resources/        # Django project settings
├── employees/             # Main application
│   ├── models.py         # Database models
│   ├── serializers.py    # API serializers
│   ├── views.py          # API views
│   ├── urls.py           # URL routing
│   └── admin.py          # Admin configuration
├── static/               # Static files
├── media/                # Media files
├── requirements.txt      # Python dependencies
├── .env                  # Development environment variables
├── .env.production       # Production environment template
└── manage.py            # Django management script
```

### Adding New Features

1. **Models**: Add new models in `employees/models.py`
2. **Serializers**: Create serializers in `employees/serializers.py`
3. **Views**: Add views in `employees/views.py`
4. **URLs**: Register URLs in `employees/urls.py`
5. **Admin**: Configure admin in `employees/admin.py`

### Database Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

## Production Deployment

1. **Environment Setup**:

   - Set `DEBUG=False`
   - Configure PostgreSQL database
   - Set strong `SECRET_KEY`

2. **Database**:

   - Install PostgreSQL
   - Create database and user
   - Update environment variables

3. **Static Files**:

   ```bash
   python manage.py collectstatic
   ```

4. **Security Considerations**:
   - Use HTTPS
   - Configure `ALLOWED_HOSTS`
   - Set up proper firewall rules
   - Use environment variables for secrets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions, please contact the development team or create an issue in the project repository.
