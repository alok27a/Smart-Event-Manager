from pydantic import BaseModel, EmailStr, Field
from pydantic_mongo import ObjectIdField
from typing import Dict, Optional
from models.event import EventCategory

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserPreferences(BaseModel):
    """Models user preferences to demonstrate learning and personalization."""
    default_reminders: Dict[EventCategory, int] = {
        EventCategory.SPORTS: 45,       # "Remind me 45 mins before sports"
        EventCategory.APPOINTMENT: 120, # "Remind me 2 hours before appointments"
    }

class User(BaseModel):
    id: ObjectIdField = Field(default_factory=ObjectIdField, alias="_id")
    email: EmailStr
    hashed_password: str
    preferences: UserPreferences = Field(default_factory=UserPreferences)

class UserPublic(BaseModel):
    id: str
    email: EmailStr
    preferences: UserPreferences


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
