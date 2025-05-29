"""Database connection and session management."""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

# Configure connection pool
engine_args = {
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_size": 5,  # Default pool size
    "max_overflow": 10,  # Maximum number of connections to exceed pool_size
    "pool_timeout": 30,  # Timeout for getting connection from pool
    "pool_recycle": 1800,  # Recycle connections after 30 minutes
}

# Add SSL configuration if specified in settings
if getattr(settings, "DB_USE_SSL", False):
    engine_args["connect_args"] = {
        "sslmode": getattr(settings, "DB_SSL_MODE", "verify-full"),
        "sslcert": getattr(settings, "DB_SSL_CERT", None),
        "sslkey": getattr(settings, "DB_SSL_KEY", None),
        "sslrootcert": getattr(settings, "DB_SSL_ROOT_CERT", None),
    }
    # Remove None values
    engine_args["connect_args"] = {k: v for k, v in engine_args["connect_args"].items() if v is not None}

# Create engine with retry capability for initial connection
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def create_db_engine() -> Engine:
    """Create database engine with retry capability."""
    try:
        return create_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            **engine_args
        )
    except Exception as e:
        print(f"Failed to create database engine: {str(e)}")
        raise

engine = create_db_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise
    finally:
        db.close()

# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Get database session.
    
    Returns:
        Generator yielding database session
    
    Raises:
        SQLAlchemyError: If database connection fails
    """
    with get_db_context() as db:
        yield db

# Set up engine event listeners for connection debugging
@event.listens_for(engine, "engine_connect")
def receive_connect(dbapi_connection, connection_record):
    """Log when a connection is created."""
    print("New database connection established")

@event.listens_for(engine, "engine_disconnect")
def receive_disconnect(dbapi_connection, connection_record):
    """Log when a connection is destroyed."""
    print("Database connection closed")
