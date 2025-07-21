from fastapi import APIRouter, HTTPException, Body, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Dict
from datetime import timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.event import EventInput, EventPublic, Reminder, ConflictCheckResponse, SharePayload, StatusUpdate
from models.user import User, UserCreate, Token, UserPublic
from services import event_service, auth_service
from core.config import settings
from core.database import get_database # Updated import

router = APIRouter()

@router.post("/users/signup", response_model=UserPublic, status_code=201, tags=["Users"])
async def signup(user_in: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    user = await auth_service.create_user(db, user_in)
    return UserPublic(id=str(user.id), email=user.email, preferences=user.preferences)

@router.post("/users/login", response_model=Token, tags=["Users"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorDatabase = Depends(get_database)):
    user = await auth_service.get_user_by_email(db, form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserPublic, tags=["Users"])
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return UserPublic(id=str(current_user.id), email=current_user.email, preferences=current_user.preferences)

@router.post("/events/parse", response_model=ConflictCheckResponse, status_code=201, tags=["Events"])
async def parse_and_create_event(event_input: EventInput, current_user: User = Depends(auth_service.get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    return await event_service.create_or_update_event(db, event_input.text, current_user=current_user)

@router.get("/events", response_model=List[EventPublic], tags=["Events"])
async def list_all_events(current_user: User = Depends(auth_service.get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    events = await event_service.get_all_events(db, owner_id=current_user.id)
    return [EventPublic(id=str(e.id), owner_id=str(e.owner_id), **e.model_dump(exclude={'id', 'owner_id'})) for e in events]


@router.get("/events/{event_id}", response_model=EventPublic, tags=["Events"])
async def get_single_event(event_id: str, current_user: User = Depends(auth_service.get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    event = await event_service.get_event_by_id(db, event_id, owner_id=current_user.id)
    if not event: raise HTTPException(status_code=404, detail="Event not found")
    return EventPublic(id=str(event.id), owner_id=str(event.owner_id), **event.model_dump(exclude={'id', 'owner_id'}))

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Events"])
async def delete_an_event(event_id: str, current_user: User = Depends(auth_service.get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    """Delete an event by its ID."""
    success = await event_service.delete_event(db, event_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/events/{event_id}/confirm", response_model=EventPublic, tags=["Event Actions"])
async def confirm_an_event(event_id: str, current_user: User = Depends(auth_service.get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    event = await event_service.confirm_event(db, event_id, owner_id=current_user.id)
    if not event: raise HTTPException(status_code=404, detail="Event not found or not updated")
    return EventPublic(id=str(event.id), owner_id=str(event.owner_id), **event.model_dump(exclude={'id', 'owner_id'}))

@router.post("/events/{event_id}/reminders", response_model=EventPublic, tags=["Event Actions"])
async def add_a_reminder(event_id: str, reminder: Reminder, current_user: User = Depends(auth_service.get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    event = await event_service.add_reminder_to_event(db, event_id, reminder, owner_id=current_user.id)
    if not event: raise HTTPException(status_code=404, detail="Event not found or not updated")
    return EventPublic(id=str(event.id), owner_id=str(event.owner_id), **event.model_dump(exclude={'id', 'owner_id'}))

@router.post("/events/{event_id}/share", response_model=SharePayload, tags=["Event Actions"])
async def share_an_event(event_id: str, share_with: List[str] = Body(..., embed=True), current_user: User = Depends(auth_service.get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    payload = await event_service.share_event(db, event_id, share_with, owner_id=current_user.id)
    if not payload: raise HTTPException(status_code=404, detail="Event not found")
    return payload

@router.get("/events/{event_id}/timeline", response_model=List[Dict], tags=["Event Actions"])
async def get_event_timeline(event_id: str, current_user: User = Depends(auth_service.get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    """Retrieve the timeline of actions for a specific event."""
    timeline = await event_service.get_event_timeline(db, event_id, owner_id=current_user.id)
    if timeline is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return timeline

@router.put("/events/{event_id}/status", response_model=EventPublic, tags=["Event Actions"])
async def update_event_status(event_id: str, status_update: StatusUpdate, current_user: User = Depends(auth_service.get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    """Manually update the status flags or state of an event."""
    event = await event_service.update_event_status(db, event_id, status_update, owner_id=current_user.id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or not updated")
    return EventPublic(id=str(event.id), owner_id=str(event.owner_id), **event.model_dump(exclude={'id', 'owner_id'}))
