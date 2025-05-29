"""Standard response models for API documentation."""
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

DataT = TypeVar("DataT")

class HTTPError(BaseModel):
    """Standard error response model."""
    detail: str

class ValidationError(BaseModel):
    """Validation error response model."""
    loc: List[str]
    msg: str
    type: str

class HTTPValidationError(BaseModel):
    """HTTP validation error response model."""
    detail: List[ValidationError]

class ResponseBase(GenericModel, Generic[DataT]):
    """Base response model."""
    data: Optional[DataT] = None
    message: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None

class PaginatedResponse(ResponseBase[DataT]):
    """Paginated response model."""
    total: int
    page: int
    size: int
    pages: int
