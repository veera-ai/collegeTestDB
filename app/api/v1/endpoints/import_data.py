"""Endpoints for bulk data import functionality."""
from typing import Any, Dict, List, Type
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import json

from app.api.v1.deps import (
    get_db,
    get_current_active_superuser,
    check_user_role
)
from app.models.user import User, UserRole
from app.schemas.import_data import (
    EntityType,
    ImportRequest,
    ImportResponse,
    ImportValidationError
)
from app.services.audit import audit_service

# Import all relevant schemas
from app.schemas.user import UserCreate
from app.schemas.academic import StudentCreate, StaffCreate
from app.schemas.records import EnrollmentCreate, GradeCreate, AttendanceCreate
from app.schemas.content import NewsCreate, EventCreate
from app.schemas.registration import RegistrationCreate
from app.schemas.monitoring import DashboardCreate, ReportCreate

# Import all relevant models
from app.models.user import User
from app.models.academic import Student, Staff
from app.models.records import Enrollment, Grade, Attendance
from app.models.content import News, Event
from app.models.registration import Registration, Report
from app.models.monitoring import Dashboard

router = APIRouter()

# Mapping of entity types to their corresponding Create schemas and models
ENTITY_MAPPINGS = {
    EntityType.USER: (UserCreate, User),
    EntityType.STUDENT: (StudentCreate, Student),
    EntityType.STAFF: (StaffCreate, Staff),
    EntityType.ENROLLMENT: (EnrollmentCreate, Enrollment),
    EntityType.GRADE: (GradeCreate, Grade),
    EntityType.ATTENDANCE: (AttendanceCreate, Attendance),
    EntityType.NEWS: (NewsCreate, News),
    EntityType.EVENT: (EventCreate, Event),
    EntityType.REGISTRATION: (RegistrationCreate, Registration),
    EntityType.DASHBOARD: (DashboardCreate, Dashboard),
    EntityType.REPORT: (ReportCreate, Report),
}

# PUBLIC_INTERFACE
@router.post(
    "/import-entity-data",
    response_model=ImportResponse,
    status_code=200,
    responses={
        200: {
            "description": "Data imported successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Data imported successfully",
                        "total_records": 10,
                        "processed_records": 8,
                        "failed_records": 2,
                        "validation_errors": [
                            {
                                "index": 3,
                                "errors": {
                                    "email": ["invalid email format"]
                                }
                            }
                        ],
                        "inserted_ids": [
                            "550e8400-e29b-41d4-a716-446655440000"
                        ]
                    }
                }
            }
        },
        400: {
            "description": "Invalid request or file format"
        },
        401: {
            "description": "Unauthorized"
        },
        403: {
            "description": "Insufficient permissions"
        }
    }
)
async def import_entity_data(
    file: UploadFile = File(...),
    entity: EntityType = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Import data for a specific entity type from a JSON file.
    
    This endpoint allows authorized users to bulk import data for various entity types.
    The data should be provided in a JSON file containing an array of objects matching
    the entity's schema.
    
    Args:
        file: JSON file containing the data to import
        entity: Type of entity to import (e.g., user, student, staff)
        db: Database session
        current_user: Current authenticated user (must be superuser)
        
    Returns:
        ImportResponse containing import results and any validation errors
    """
    try:
        # Read and parse the JSON file
        content = await file.read()
        data = json.loads(content.decode())
        
        if not isinstance(data, list):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Expected JSON array of objects."
            )
            
        schema_class, model_class = ENTITY_MAPPINGS[entity]
        validation_errors: List[ImportValidationError] = []
        inserted_ids: List[str] = []
        processed_count = 0
        
        # Process each record
        for index, record in enumerate(data):
            try:
                # Validate using Pydantic schema
                validated_data = schema_class(**record)
                
                # Convert to ORM model
                db_obj = model_class(**validated_data.dict())
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                
                inserted_ids.append(str(db_obj.id))
                processed_count += 1
                
            except Exception as e:
                validation_errors.append(
                    ImportValidationError(
                        index=index,
                        errors={"_error": [str(e)]}
                    )
                )
                db.rollback()
                
        # Log the import activity
        audit_service.log_activity(
            db=db,
            user=current_user,
            action="bulk_import",
            entity_type=entity.value,
            entity_id="multiple",
            changes={
                "total_records": len(data),
                "processed_records": processed_count,
                "failed_records": len(validation_errors)
            },
            details=f"Bulk import of {entity.value} data by {current_user.username}"
        )
        
        return ImportResponse(
            success=True,
            message="Data import completed",
            total_records=len(data),
            processed_records=processed_count,
            failed_records=len(validation_errors),
            validation_errors=validation_errors,
            inserted_ids=inserted_ids
        )
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format in uploaded file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing import: {str(e)}"
        )
