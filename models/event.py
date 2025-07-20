from pydantic import BaseModel, Field
from pydantic_mongo import ObjectIdField
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum

class EventState(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    SHARED = "SHARED"
    REMINDER_SENT = "REMINDER_SENT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class EventCategory(str, Enum):
    """Represents learned categories for events to drive smart actions."""
    UNCATEGORIZED = "UNCATEGORIZED"
    SPORTS = "SPORTS"
    APPOINTMENT = "APPOINTMENT"
    SCHOOL = "SCHOOL"
    WORK = "WORK"
    SOCIAL = "SOCIAL"

class EventInput(BaseModel):
    text: str = Field(..., example="reschedule Chuck’s soccer game to Thursday at 3:30pm at Sunset Field")

class Reminder(BaseModel):
    minutes_before: int = Field(..., example=30)
    message: Optional[str] = Field(None, example="Time to leave for soccer!")

class Event(BaseModel):
    id: ObjectIdField = Field(default_factory=ObjectIdField, alias="_id")
    owner_id: ObjectIdField
    title: str = Field(..., example="Chuck's soccer game")
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, example="Sunset Field")
    notes: Optional[str] = None
    category: EventCategory = EventCategory.UNCATEGORIZED
    state: EventState = Field(default=EventState.DRAFT)
    reminders: List[Reminder] = []
    timeline: List[Dict] = Field(default_factory=list)
    is_confirmed: bool = False
    was_shared: bool = False
    is_reminded: bool = False

class EventPublic(BaseModel):
    id: str
    owner_id: str
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    category: EventCategory
    state: EventState
    reminders: List[Reminder]
    timeline: List[Dict]


class ConflictCheckResponse(BaseModel):
    is_conflict: bool
    conflict_details: Optional[str] = None
    created_event: EventPublic

class SharePayload(BaseModel):
    summary: str
    start: datetime
    location: Optional[str]
    notes: Optional[str]

class StatusUpdate(BaseModel):
    """Model for updating the status of an event."""
    state: Optional[EventState] = None
    is_confirmed: Optional[bool] = None
    is_reminded: Optional[bool] = None
    was_shared: Optional[bool] = None
