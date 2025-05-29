# College Portal - ColorCraft Container

This is the main monolithic application container for the College Portal, providing a comprehensive REST API for managing college operations.

## Features

- RESTful API with OpenAPI 3.0 documentation
- Secure authentication using JWT/OAuth2
- Role-based access control (RBAC)
- Entity management (Users, Students, etc.)
- Advanced search and filtering
- Audit logging
- Academic record management
- Event and registration handling
- Dashboard and reporting

## Tech Stack

- FastAPI (Web Framework)
- SQLAlchemy (ORM)
- Pydantic (Data Validation)
- PostgreSQL (Database)
- JWT (Authentication)
- Uvicorn (ASGI Server)

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- Virtual environment tool (venv or conda)

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables by creating a `.env` file:
```ini
# Project settings
PROJECT_NAME="College Portal API"
VERSION="1.0.0"
API_V1_STR="/api/v1"

# Security
SECRET_KEY="your-secret-key-here"  # Change this to a secure value
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database configuration
# You can use either the standard DB_* variables:
DB_HOST="localhost"
DB_PORT=5432  # Optional, defaults to 5432
DB_USER="your_db_user"
DB_PASS="your_db_password"
DB_NAME="college_portal"

# Or the legacy POSTGRES_* variables (maintained for backward compatibility):
# POSTGRES_SERVER="localhost"
# POSTGRES_USER="your_db_user"
# POSTGRES_PASSWORD="your_db_password"
# POSTGRES_DB="college_portal"

# CORS Settings (comma-separated list of origins)
BACKEND_CORS_ORIGINS="http://localhost,http://localhost:8080,http://localhost:3000"
```

4. Database Setup:
   
   a. Create the MySQL database:
   ```bash
   mysql -u root -p
   CREATE DATABASE college_portal;
   CREATE USER 'your_db_user'@'localhost' IDENTIFIED BY 'your_db_password';
   GRANT ALL PRIVILEGES ON college_portal.* TO 'your_db_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

   b. The application will automatically create the necessary tables on first run.

5. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── api/              # API endpoints
│   └── v1/          # API version 1
│       ├── endpoints/   # Route handlers
│       ├── deps.py     # Dependencies
│       └── api.py      # Router setup
├── core/            # Core functionality
│   ├── config.py    # Configuration
│   ├── database.py  # Database setup
│   └── security.py  # Security utilities
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
└── services/        # Business logic
```

## Available Endpoints

- `/api/v1/auth/*` - Authentication operations
- `/api/v1/users/*` - User management
- `/api/v1/academic/*` - Academic operations
- `/api/v1/records/*` - Student records
- `/api/v1/content/*` - News and events
- `/api/v1/registration/*` - Event registration
- `/api/v1/monitoring/*` - System monitoring

## Development Guidelines

- Follow PEP 8 style guide
- Write docstrings for all public interfaces
- Add tests for new features
- Update documentation as needed
- Use type hints
- Follow git commit message conventions

## Troubleshooting

1. Database Connection Issues:
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists and user has proper permissions

2. API Access Issues:
   - Verify JWT token is valid
   - Check user roles and permissions
   - Ensure CORS origins are properly configured

3. Common Error Codes:
   - 401: Authentication required
   - 403: Insufficient permissions
   - 404: Resource not found
   - 422: Validation error
   - 500: Server error

## Security Notes

- Always use HTTPS in production
- Regularly rotate JWT secrets
- Keep dependencies updated
- Monitor audit logs
- Follow security best practices for PostgreSQL
