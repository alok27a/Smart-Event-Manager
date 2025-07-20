from models.event import EventCategory

def categorize_event(title: str) -> EventCategory:
    """
    A simple agentic function to categorize an event.
    This demonstrates the system's ability to enrich data beyond simple parsing.
    A more advanced version would use another LLM call for more nuanced classification.
    """
    title_lower = title.lower()
    if any(keyword in title_lower for keyword in ["soccer", "practice", "game", "match"]):
        return EventCategory.SPORTS
    if any(keyword in title_lower for keyword in ["doctor", "dentist", "appointment"]):
        return EventCategory.APPOINTMENT
    if any(keyword in title_lower for keyword in ["school", "pta", "parent-teacher"]):
        return EventCategory.SCHOOL
    if any(keyword in title_lower for keyword in ["meeting", "work", "call"]):
        return EventCategory.WORK
    if any(keyword in title_lower for keyword in ["party", "dinner", "get-together"]):
        return EventCategory.SOCIAL
    return EventCategory.UNCATEGORIZED

