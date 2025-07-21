from typing import Dict, Optional, List
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.event import Event, EventPublic, ConflictCheckResponse, Reminder, SharePayload, EventState, StatusUpdate
from services import nlp_service, calendar_service, assistant_service
from models.user import User

async def create_event(db: AsyncIOMotorDatabase, text: str, current_user: User) -> ConflictCheckResponse:
    # 1. Parse the event using the LLM
    parsed_details = await nlp_service.parse_event_from_text(text)
    
    # 2. Agentic Step: Categorize the event
    category = assistant_service.categorize_event(parsed_details.title)
    
    # 3. Create a new event
    event_instance = await _create_new_event(db, parsed_details, category, current_user)

    # 4. Check for conflicts against the user's other events
    user_events_cursor = db.events.find({"owner_id": current_user.id})
    user_events = [Event(**doc) async for doc in user_events_cursor]
    conflicting_event = calendar_service.check_conflict(event_instance, user_events)
    
    suggested_times = []
    if conflicting_event:
        duration = event_instance.end_time - event_instance.start_time
        suggested_times = calendar_service.find_next_available_slots(
            start_time=conflicting_event.end_time,
            duration=duration,
            existing_events=user_events
        )

    conflict_details_str = f"Conflicts with '{conflicting_event.title}'" if conflicting_event else None
    
    # Convert to public model for response
    public_event = EventPublic(
        id=str(event_instance.id),
        owner_id=str(event_instance.owner_id),
        title=event_instance.title,
        start_time=event_instance.start_time,
        end_time=event_instance.end_time,
        location=event_instance.location,
        notes=event_instance.notes,
        category=event_instance.category,
        state=event_instance.state,
        reminders=event_instance.reminders,
        timeline=event_instance.timeline
    )

    return ConflictCheckResponse(is_conflict=bool(conflicting_event), conflict_details=conflict_details_str, created_event=public_event, suggested_times=suggested_times)


async def _create_new_event(db: AsyncIOMotorDatabase, parsed_details: nlp_service.ParsedEventDetails, category: assistant_service.EventCategory, current_user: User) -> Event:
    note_about_category = f"Assistant classified this as: {category.value}."
    if parsed_details.notes:
        parsed_details.notes += f"\n{note_about_category}"
    else:
        parsed_details.notes = note_about_category

    event_data = Event(
        owner_id=current_user.id,
        title=parsed_details.title,
        start_time=parsed_details.start_time,
        end_time=parsed_details.end_time,
        location=parsed_details.location,
        notes=parsed_details.notes,
        category=category,
        timeline=[{
            "timestamp": datetime.utcnow().isoformat(),
            "action": "Event Created",
            "details": f"Category: {category.value}"
        }]
    )
    
    insert_result = await db.events.insert_one(event_data.model_dump(by_alias=True))
    event_data.id = insert_result.inserted_id
    return event_data


async def get_event_by_id(db: AsyncIOMotorDatabase, event_id: str, owner_id: ObjectId) -> Optional[Event]:
    event_doc = await db.events.find_one({"_id": ObjectId(event_id), "owner_id": owner_id})
    if event_doc:
        return Event(**event_doc)
    return None

async def get_all_events(db: AsyncIOMotorDatabase, owner_id: ObjectId) -> List[Event]:
    events = []
    cursor = db.events.find({"owner_id": owner_id})
    async for document in cursor:
        events.append(Event(**document))
    return events

async def confirm_event(db: AsyncIOMotorDatabase, event_id: str, owner_id: ObjectId) -> Optional[Event]:
    event = await get_event_by_id(db, event_id, owner_id)
    if not event: return None
    
    update_result = await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {
            "$set": {"state": EventState.CONFIRMED, "is_confirmed": True},
            "$push": {"timeline": {"timestamp": datetime.utcnow().isoformat(), "action": "Event Confirmed"}}
        }
    )
    if update_result.modified_count:
        return await get_event_by_id(db, event_id, owner_id)
    return None

async def reschedule_event(db: AsyncIOMotorDatabase, event_id: str, text: str, current_user: User) -> Optional[Event]:
    original_event = await get_event_by_id(db, event_id, current_user.id)
    if not original_event:
        return None

    parsed_details = await nlp_service.parse_event_from_text(text)

    update_data = {
        "start_time": parsed_details.start_time,
        "end_time": parsed_details.end_time,
        "location": parsed_details.location or original_event.location,
        "notes": parsed_details.notes or original_event.notes,
        "state": EventState.DRAFT,
        "is_confirmed": False,
    }
    
    update_result = await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {
            "$set": update_data,
            "$push": {"timeline": {"timestamp": datetime.utcnow().isoformat(), "action": "Event Rescheduled", "details": f"New time: {parsed_details.start_time}"}}
        }
    )
    if update_result.modified_count:
        return await get_event_by_id(db, event_id, current_user.id)
    return None


async def add_reminder_to_event(db: AsyncIOMotorDatabase, event_id: str, reminder: Reminder, owner_id: ObjectId) -> Optional[Event]:
    update_result = await db.events.update_one(
        {"_id": ObjectId(event_id), "owner_id": owner_id},
        {
            "$push": {
                "reminders": reminder.model_dump(),
                "timeline": {"timestamp": datetime.utcnow().isoformat(), "action": "Reminder Added"}
            }
        }
    )
    if update_result.modified_count:
        return await get_event_by_id(db, event_id, owner_id)
    return None

async def share_event(db: AsyncIOMotorDatabase, event_id: str, share_with: List[str], owner_id: ObjectId) -> Optional[SharePayload]:
    event = await get_event_by_id(db, event_id, owner_id)
    if not event: return None
    
    await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {
            "$set": {"state": EventState.SHARED, "was_shared": True},
            "$push": {"timeline": {"timestamp": datetime.utcnow().isoformat(), "action": "Event Shared", "details": f"Simulated sharing with: {', '.join(share_with)}"}}
        }
    )
    
    return SharePayload(summary=f"Event: {event.title}", start=event.start_time, location=event.location, notes=event.notes)

async def get_event_timeline(db: AsyncIOMotorDatabase, event_id: str, owner_id: ObjectId) -> Optional[List[Dict]]:
    event = await get_event_by_id(db, event_id, owner_id)
    if event:
        return event.timeline
    return None

async def update_event_status(db: AsyncIOMotorDatabase, event_id: str, status_update: StatusUpdate, owner_id: ObjectId) -> Optional[Event]:
    update_data = status_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No status information provided")

    update_result = await db.events.update_one(
        {"_id": ObjectId(event_id), "owner_id": owner_id},
        {
            "$set": update_data,
            "$push": {"timeline": {"timestamp": datetime.utcnow().isoformat(), "action": "Status Updated", "details": f"New status: {update_data}"}}
        }
    )
    if update_result.modified_count:
        return await get_event_by_id(db, event_id, owner_id)
    return None

async def delete_event(db: AsyncIOMotorDatabase, event_id: str, owner_id: ObjectId) -> bool:
    delete_result = await db.events.delete_one({"_id": ObjectId(event_id), "owner_id": owner_id})
    return delete_result.deleted_count > 0
