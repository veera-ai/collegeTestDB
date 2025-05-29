# College Portal - ColorCraft Container

This is the main monolithic application container for the College Portal, providing a comprehensive REST API for managing college operations.

## Features

- RESTful API with OpenAPI 3.0 documentation
- Secure authentication using JWT/OAuth2
- Role-based access control (RBAC)
- Entity management (Users, Students, etc.)
- Advanced search and filtering
- Audit logging

## Tech Stack

- FastAPI (Web Framework)
- SQLAlchemy (ORM)
- Pydantic (Data Validation)
- PostgreSQL (Database)
- JWT (Authentication)

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
uvicorn app.main:app --reload
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
├── core/            # Core functionality
├── models/          # Database models
├── schemas/         # Pydantic schemas
└── services/        # Business logic
```

## Development

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation as needed
