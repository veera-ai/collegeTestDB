from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, MySQLDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "College Portal API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:8001"
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str], None]) -> Union[List[str], str, None]:
        if v is None:
            return None
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database Configuration
    # Support both standard DB_* and legacy POSTGRES_* environment variables
    DB_HOST: str = "testdb.c96s4aykk9hv.us-east-1.rds.amazonaws.com"
    DB_PORT: int = 3306  # Default MySQL port
    DB_USER: str = "admin"
    DB_PASS: str = "pu90c8kV9QoN6j"
    DB_NAME: str = "testdb"
    
    # Database SSL Configuration
    DB_USE_SSL: bool = False
    DB_SSL_MODE: str = "VERIFY_IDENTITY"  # MySQL SSL modes: DISABLED, PREFERRED, REQUIRED, VERIFY_CA, VERIFY_IDENTITY
    DB_SSL_CERT: Optional[str] = None  # Path to client certificate
    DB_SSL_KEY: Optional[str] = None   # Path to client key
    DB_SSL_ROOT_CERT: Optional[str] = None  # Path to root certificate (CA)
    
    # Database Pool Configuration
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # 30 minutes
    
    # Legacy variables (maintained for backward compatibility)
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
