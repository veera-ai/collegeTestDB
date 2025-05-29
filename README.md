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
# Primary database connection variables:
DB_HOST="localhost"
DB_PORT=3306  # Optional, defaults to 3306 for MySQL
DB_USER="your_db_user"
DB_PASS="your_db_password"
DB_NAME="college_portal"

# Legacy variables (maintained for backward compatibility):
# POSTGRES_SERVER="localhost"  # Will be used as fallback for DB_HOST
# POSTGRES_USER="your_db_user"  # Will be used as fallback for DB_USER
# POSTGRES_PASSWORD="your_db_password"  # Will be used as fallback for DB_PASS
# POSTGRES_DB="college_portal"  # Will be used as fallback for DB_NAME

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

## Database Initialization & Running Locally

### MySQL Installation and Setup

1. Install MySQL 8.0+:
   - **Ubuntu/Debian**: `sudo apt install mysql-server`
   - **macOS**: Using Homebrew: `brew install mysql`
   - **Windows**: Download and install from [MySQL Official Website](https://dev.mysql.com/downloads/mysql/)

2. Start MySQL service:
   - **Ubuntu/Debian**: `sudo systemctl start mysql`
   - **macOS**: `brew services start mysql`
   - **Windows**: MySQL service starts automatically after installation

3. Set root password (if not set during installation):
   ```bash
   sudo mysql_secure_installation
   ```

### Database Creation and User Setup

1. Log into MySQL as root:
   ```bash
   mysql -u root -p
   ```

2. Create database and user:
   ```sql
   CREATE DATABASE college_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'college_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON college_portal.* TO 'college_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Schema Initialization

The application uses SQLAlchemy ORM for database management. The schema can be initialized in two ways:

1. **Auto-create on First Run (Default)**:
   - The tables will be automatically created when the application starts
   - This is handled by the SQLAlchemy ORM based on the models defined in `app/models/`
   - Ensure your database user has the necessary privileges

2. **Using entity-schema.json**:
   - The file `entity-schema.json` contains the complete database schema definition
   - This can be used as a reference for the database structure
   - The schema is automatically synchronized with the SQLAlchemy models

### Environment Setup

1. Create a `.env` file in the project root with the following content:
   ```ini
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=college_user
   DB_PASS=your_secure_password
   DB_NAME=college_portal
   
   # Security Settings
   SECRET_KEY=your-secure-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # API Settings
   PROJECT_NAME="College Portal API"
   VERSION="1.0.0"
   API_V1_STR="/api/v1"
   
   # CORS Settings
   BACKEND_CORS_ORIGINS="http://localhost,http://localhost:8080,http://localhost:3000"
   ```

### Running the Application

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Database Connection Troubleshooting

1. **Connection Refused**:
   - Verify MySQL is running: 
     ```bash
     # Linux
     sudo systemctl status mysql
     # macOS
     brew services list
     # Windows
     net start mysql80
     ```
   - Check host and port in `.env` file
   - Ensure MySQL is accepting connections:
     ```bash
     sudo netstat -tlnp | grep mysql
     ```

2. **Access Denied**:
   - Verify username and password in `.env`
   - Check user privileges:
     ```sql
     SHOW GRANTS FOR 'college_user'@'localhost';
     ```
   - Reset user privileges if needed:
     ```sql
     GRANT ALL PRIVILEGES ON college_portal.* TO 'college_user'@'localhost';
     FLUSH PRIVILEGES;
     ```

3. **Database Does Not Exist**:
   - Verify database name in `.env`
   - Create database if missing:
     ```sql
     CREATE DATABASE college_portal;
     ```

4. **Table Creation Errors**:
   - Check user has CREATE privileges:
     ```sql
     GRANT CREATE ON college_portal.* TO 'college_user'@'localhost';
     ```
   - Clear any partial tables:
     ```sql
     DROP DATABASE college_portal;
     CREATE DATABASE college_portal;
     ```

5. **SSL/TLS Issues**:
   - If using SSL, verify SSL settings in `.env`:
     ```ini
     DB_USE_SSL=True
     DB_SSL_MODE=VERIFY_IDENTITY
     DB_SSL_CERT=/path/to/client-cert.pem
     DB_SSL_KEY=/path/to/client-key.pem
     DB_SSL_ROOT_CERT=/path/to/ca.pem
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
   - Verify MySQL is running
   - Check database credentials in `.env`
   - Ensure database exists and user has proper permissions
   - Check MySQL connection timeout settings if experiencing intermittent disconnects

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
- Follow security best practices for MySQL
