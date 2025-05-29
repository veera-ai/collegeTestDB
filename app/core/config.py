from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


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
    DB_PORT: Optional[int] = 5432
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None
    
    # Legacy variables (maintained for backward compatibility)
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
            
        # Get host from DB_HOST or fall back to POSTGRES_SERVER
        host = values.get("DB_HOST") or values.get("POSTGRES_SERVER")
        if not host:
            raise ValueError("Database host must be specified via DB_HOST or POSTGRES_SERVER")
            
        # Get user from DB_USER or fall back to POSTGRES_USER
        user = values.get("DB_USER") or values.get("POSTGRES_USER")
        if not user:
            raise ValueError("Database user must be specified via DB_USER or POSTGRES_USER")
            
        # Get password from DB_PASS or fall back to POSTGRES_PASSWORD
        password = values.get("DB_PASS") or values.get("POSTGRES_PASSWORD")
        if not password:
            raise ValueError("Database password must be specified via DB_PASS or POSTGRES_PASSWORD")
            
        # Get database name from DB_NAME or fall back to POSTGRES_DB
        db_name = values.get("DB_NAME") or values.get("POSTGRES_DB")
        if not db_name:
            raise ValueError("Database name must be specified via DB_NAME or POSTGRES_DB")
            
        # Get port from DB_PORT (defaults to 5432 if not specified)
        port = str(values.get("DB_PORT", 5432))
        
        return PostgresDsn.build(
            scheme="postgresql",
            user=user,
            password=password,
            host=host,
            port=port,
            path=f"/{db_name}",
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
