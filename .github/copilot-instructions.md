# Copilot Instructions for Human Resources Django Project

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a Django REST Framework project for human resources management called "human-resources". The project includes:

- Employee management system
- Department organization
- REST API endpoints with Django REST Framework
- Environment-based configuration (development and production)
- SQLite for development, PostgreSQL for production

## Development Guidelines

### Environment Configuration
- Use `.env` file for development environment variables
- Use `.env.production` for production environment variables
- Always use environment variables for sensitive data like SECRET_KEY and database credentials

### Database
- Development: SQLite (default, already configured)
- Production: PostgreSQL (configure via environment variables)

### API Design
- Follow REST principles
- Use ViewSets for CRUD operations
- Implement proper filtering, searching, and pagination
- Include proper error handling and validation

### Code Style
- Follow Django best practices
- Use proper model relationships
- Implement comprehensive serializers
- Add proper admin interface configurations
- Include docstrings for classes and methods

### Security
- Never commit sensitive data like SECRET_KEY or passwords
- Use Django's built-in authentication and permissions
- Validate all user inputs
- Follow Django security best practices

### Testing
- Write unit tests for models, serializers, and views
- Use Django's testing framework
- Test API endpoints thoroughly
- Include edge cases and error conditions

## Key Files
- `human_resources/settings.py` - Main Django settings with environment variable support
- `employees/models.py` - Employee and Department models
- `employees/serializers.py` - API serializers
- `employees/views.py` - API views and ViewSets
- `employees/admin.py` - Django admin configuration
- `.env` - Development environment variables
- `.env.production` - Production environment variables template
