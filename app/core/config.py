from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, MySQLDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "College Portal API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
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
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = 3306  # Default MySQL port
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None
    
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
    
    SQLALCHEMY_DATABASE_URI: Optional[MySQLDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
            
        # Get host from DB_HOST or fall back to legacy server
        host = values.get("DB_HOST") or values.get("POSTGRES_SERVER")
        if not host:
            raise ValueError("Database host must be specified via DB_HOST")
            
        # Get user from DB_USER or fall back to legacy user
        user = values.get("DB_USER") or values.get("POSTGRES_USER")
        if not user:
            raise ValueError("Database user must be specified via DB_USER")
            
        # Get password from DB_PASS or fall back to legacy password
        password = values.get("DB_PASS") or values.get("POSTGRES_PASSWORD")
        if not password:
            raise ValueError("Database password must be specified via DB_PASS")
            
        # Get database name from DB_NAME or fall back to legacy db
        db_name = values.get("DB_NAME") or values.get("POSTGRES_DB")
        if not db_name:
            raise ValueError("Database name must be specified via DB_NAME")
            
        # Get port from DB_PORT (defaults to 3306 for MySQL)
        port = str(values.get("DB_PORT", 3306))
        
        # Build MySQL DSN
        dsn = MySQLDsn.build(
            scheme="mysql+mysqlconnector",  # Using mysql-connector-python
            user=user,
            password=password,
            host=host,
            port=port,
            path=f"/{db_name}",
        )

        # Add MySQL SSL options if enabled
        if values.get("DB_USE_SSL"):
            ssl_mode = values.get("DB_SSL_MODE", "VERIFY_IDENTITY")
            query_params = [f"ssl_mode={ssl_mode}"]
            
            # Add SSL certificate paths if provided
            if values.get("DB_SSL_CERT"):
                query_params.append(f"ssl_cert={values['DB_SSL_CERT']}")
            if values.get("DB_SSL_KEY"):
                query_params.append(f"ssl_key={values['DB_SSL_KEY']}")
            if values.get("DB_SSL_ROOT_CERT"):
                query_params.append(f"ssl_ca={values['DB_SSL_ROOT_CERT']}")
            
            # Append query parameters to DSN
            if query_params:
                dsn = f"{dsn}?{'&'.join(query_params)}"
        
        return dsn

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
