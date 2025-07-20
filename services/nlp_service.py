import json
from openai import AsyncOpenAI
from datetime import datetime, timedelta # <--- THE FIX IS HERE
from typing import Optional
from pydantic import BaseModel, Field
from models.event import Event
from core.config import settings

# Initialize the modern, v1.x client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class ParsedEventDetails(BaseModel):
    """A model for the LLM to populate."""
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    is_reschedule: bool = Field(default=False, description="Set to true if the text mentions 'reschedule', 'move', 'change', or similar terms.")


async def parse_event_from_text(text: str) -> ParsedEventDetails:
    """
    Uses the OpenAI API (v1.x) with Tools to parse unstructured text,
    ensuring an end_time is always present and detecting reschedule intent.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_event",
                "description": "Extracts event details from a user's text, including intent to reschedule.",
                "parameters": ParsedEventDetails.model_json_schema(by_alias=True)
            }
        }
    ]

    prompt = f"""
    The current date is {datetime.now().strftime('%A, %Y-%m-%d')}.
    Analyze the following text: "{text}".
    Extract the event details. Pay close attention to keywords like 'reschedule', 'move', 'postpone', 'change' to determine if this is an update to an existing event.
    If an end time is not specified, predict a reasonable duration based on the event's title and context
    (e.g., a meeting is usually 60 minutes, a soccer game 90 minutes, a party 3 hours)
    and calculate the `end_time`.
    """

    try:
        # --- REAL API CALL using modern client ---
        response = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "create_event"}}
        )
        
        message = response.choices[0].message
        tool_calls = message.tool_calls
        
        if tool_calls:
            arguments = json.loads(tool_calls[0].function.arguments)
            parsed_details = ParsedEventDetails(**arguments)

            # Agentic Step: Ensure an end_time exists.
            if parsed_details.end_time is None:
                parsed_details.end_time = parsed_details.start_time + timedelta(hours=1)
            
            return parsed_details
        else:
            raise ValueError("OpenAI did not return a tool call.")

    except Exception as e:
        print(f"Error calling OpenAI or parsing response: {e}")
        # Return a default object on failure
        return ParsedEventDetails(
            title="Could not parse event",
            start_time=datetime.now() + timedelta(hours=1),
            end_time=datetime.now() + timedelta(hours=2),
            notes=f"Original text: '{text}'. Error during parsing."
        )
