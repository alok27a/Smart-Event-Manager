from typing import List, Optional
from datetime import datetime
from models.event import Event

MOCKED_CALENDAR_EVENTS: List[Event] = [] # This is now less important as conflicts are checked against user's own events

def check_conflict(new_event: Event, existing_events: List[Event]) -> Optional[Event]:
    for existing_event in existing_events:
        # Don't check for conflict with itself
        if new_event.id and new_event.id == existing_event.id:
            continue
        if existing_event.end_time and new_event.end_time:
            if new_event.start_time < existing_event.end_time and new_event.end_time > existing_event.start_time:
                return existing_event
    return None
