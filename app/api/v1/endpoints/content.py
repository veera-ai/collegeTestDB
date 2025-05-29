"""Content management endpoints for news and events."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    check_user_role
)
from app.models.user import User, UserRole
from app.models.content import News, Event, NewsCategory, EventStatus
from app.schemas.content import (
    News as NewsSchema,
    NewsCreate,
    NewsUpdate,
    Event as EventSchema,
    EventCreate,
    EventUpdate
)

router = APIRouter()

# News endpoints
# PUBLIC_INTERFACE
@router.get("/news/", response_model=List[NewsSchema])
def get_news(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get list of news items."""
    news_items = db.query(News).offset(skip).limit(limit).all()
    return news_items

# PUBLIC_INTERFACE
@router.post("/news/", response_model=NewsSchema)
def create_news(
    *,
    db: Session = Depends(get_db),
    news_in: NewsCreate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Create new news item."""
    news = News(**news_in.dict())
    db.add(news)
    db.commit()
    db.refresh(news)
    return news

# PUBLIC_INTERFACE
@router.get("/news/{news_id}", response_model=NewsSchema)
def get_news_item(
    news_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get news item by ID."""
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return news

# PUBLIC_INTERFACE
@router.put("/news/{news_id}", response_model=NewsSchema)
def update_news(
    *,
    db: Session = Depends(get_db),
    news_id: str,
    news_in: NewsUpdate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Update news item."""
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    
    # Only author or admin can update news
    if not current_user.is_superuser and news.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this news item"
        )
    
    for field, value in news_in.dict(exclude_unset=True).items():
        setattr(news, field, value)
    
    db.add(news)
    db.commit()
    db.refresh(news)
    return news

# PUBLIC_INTERFACE
@router.delete("/news/{news_id}", response_model=NewsSchema)
def delete_news(
    *,
    db: Session = Depends(get_db),
    news_id: str,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Delete news item."""
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    
    # Only author or admin can delete news
    if not current_user.is_superuser and news.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this news item"
        )
    
    db.delete(news)
    db.commit()
    return news

# Event endpoints
# PUBLIC_INTERFACE
@router.get("/events/", response_model=List[EventSchema])
def get_events(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get list of events."""
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

# PUBLIC_INTERFACE
@router.post("/events/", response_model=EventSchema)
def create_event(
    *,
    db: Session = Depends(get_db),
    event_in: EventCreate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Create new event."""
    # Validate event dates
    if event_in.end_time <= event_in.start_time:
        raise HTTPException(
            status_code=400,
            detail="Event end time must be after start time"
        )
    
    event = Event(**event_in.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

# PUBLIC_INTERFACE
@router.get("/events/{event_id}", response_model=EventSchema)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get event by ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# PUBLIC_INTERFACE
@router.put("/events/{event_id}", response_model=EventSchema)
def update_event(
    *,
    db: Session = Depends(get_db),
    event_id: str,
    event_in: EventUpdate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Update event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Only organizer or admin can update event
    if not current_user.is_superuser and event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this event"
        )
    
    # Validate event dates if being updated
    if event_in.end_time and event_in.start_time:
        if event_in.end_time <= event_in.start_time:
            raise HTTPException(
                status_code=400,
                detail="Event end time must be after start time"
            )
    
    for field, value in event_in.dict(exclude_unset=True).items():
        setattr(event, field, value)
    
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

# PUBLIC_INTERFACE
@router.delete("/events/{event_id}", response_model=EventSchema)
def delete_event(
    *,
    db: Session = Depends(get_db),
    event_id: str,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Delete event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Only organizer or admin can delete event
    if not current_user.is_superuser and event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this event"
        )
    
    db.delete(event)
    db.commit()
    return event
