from typing import List, Optional
from datetime import datetime, timedelta
from models.event import Event

def check_conflict(new_event: Event, existing_events: List[Event]) -> Optional[Event]:
    for existing_event in existing_events:
        # Don't check for conflict with itself
        if new_event.id and new_event.id == existing_event.id:
            continue
        if existing_event.end_time and new_event.end_time:
            if new_event.start_time < existing_event.end_time and new_event.end_time > existing_event.start_time:
                return existing_event
    return None

def find_next_available_slots(
    start_time: datetime,
    duration: timedelta,
    existing_events: List[Event],
    count: int = 3
) -> List[datetime]:
    """
    Finds the next available time slots on a calendar.
    """
    suggestions = []
    
    # Sort events by start time to make scanning easier
    sorted_events = sorted(existing_events, key=lambda e: e.start_time)
    
    # Start looking for slots from the end of the conflicting event or 30 mins from now
    search_time = max(start_time, datetime.now() + timedelta(minutes=30))

    while len(suggestions) < count:
        # Round up to the next 15-minute interval
        search_time += timedelta(minutes=(15 - search_time.minute % 15))

        # Define the potential new event's time window
        potential_end_time = search_time + duration
        
        # Check if the slot is within reasonable hours (e.g., 8am to 10pm)
        if not (8 <= search_time.hour < 22):
            # If it's too late, jump to 8am the next day
            search_time = search_time.replace(hour=8, minute=0, second=0) + timedelta(days=1)
            continue

        # Check for conflicts with existing events
        is_free = True
        for event in sorted_events:
            if search_time < event.end_time and potential_end_time > event.start_time:
                is_free = False
                # Jump search time to the end of the conflicting event
                search_time = event.end_time
                break
        
        if is_free:
            suggestions.append(search_time)
            # Move to the next slot after the one we just found
            search_time = potential_end_time

    return suggestions
