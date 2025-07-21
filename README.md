Family Event Assistant
======================

This project is a full-stack application designed to be a "smart assistant" for managing family logistics. It features a FastAPI backend that uses AI to parse unstructured text into structured calendar events and a React frontend with Chakra UI for a user-friendly interface. The system is built around an agentic workflow, where it not only captures events but also handles conflicts, makes intelligent suggestions, and manages the event lifecycle.

How to Run the Project
----------------------

### Backend (FastAPI)

1.  **Navigate to the Backend Directory:**

    ```
    cd path/to/your/backend/folder

    ```

2.  **Install Dependencies:**

    ```
    pip install "fastapi[all]" uvicorn "python-jose[cryptography]" motor "pydantic-mongo>=0.2.0" "openai>=1.0" "passlib[bcrypt]"

    ```

3.  **Set Up Environment Variables:**

    -   Create a `.env` file in the backend's root directory.

    -   Add the following keys, replacing the placeholder values with your actual credentials:

        ```
        SECRET_KEY=your_super_secret_random_string
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        OPENAI_API_KEY="your_openai_api_key_here"
        MONGO_CONNECTION_STRING="your_mongodb_connection_string_here"

        ```

4.  **Run the Server:**

    ```
    uvicorn main:app --reload

    ```

    The backend API will be running at `http://127.0.0.1:8000`.

### Frontend (React)

1.  **Navigate to the Frontend Directory:**

    ```
    cd path/to/your/frontend/folder

    ```

2.  **Install Dependencies:**

    ```
    npm install

    ```

    *If you encounter a module error for `date-fns`, run:*

    ```
    npm install date-fns

    ```

3.  **Run the Application:**

    ```
    npm start

    ```

    The frontend will be available at `http://localhost:3000`.

What's Mocked vs. Functional
----------------------------

### Functional

-   **Full-Stack CRUD Operations:** The application fully supports creating, reading, updating, and deleting events.

-   **User Authentication:** A complete sign-up and login system using JWT for secure, persistent sessions.

-   **AI-Powered Event Parsing:** Live integration with the OpenAI API to parse unstructured text into structured event data, including title, time, location, and rescheduling intent.

-   **Persistent Database:** All user and event data is stored in a MongoDB database, ensuring data is saved between sessions.

-   **Smart Conflict Detection:** The system checks for scheduling conflicts against a user's actual events in the database.

-   **Proactive Rescheduling Suggestions:** When a conflict is detected, the backend intelligently finds and suggests the next three available time slots.

-   **ID-Based Rescheduling:** A robust rescheduling workflow that updates events based on their unique ID, initiated from the event details view.

-   **Event Lifecycle Management:** Full support for managing event states (e.g., `DRAFT`, `CONFIRMED`, `CANCELLED`), adding reminders, and simulating sharing.

### Mocked

-   **Calendar Integration for Conflict Checking:** While the system checks for conflicts against its own database, it does not yet connect to external calendars like Google Calendar or Outlook to see a user's full schedule. The `calendar_service.py` is designed to be the integration point for this.

Tradeoffs and Assumptions
-------------------------

-   **Single-User Calendar Context:** The system currently operates within its own ecosystem. It assumes all relevant events are created within the application. A production version would require two-way sync with external calendar providers.

-   **Simplified Reschedule Search:** When a reschedule request is made via natural language (e.g., "reschedule the meeting"), the backend's search for the original event is based on a simple title match. This was a tradeoff for speed and simplicity; a more advanced system would use fuzzy matching or require the user to explicitly select the event to reschedule (which is the flow now supported via the UI).

-   **Synchronous Operations:** While the application uses `async` and `await`, long-running tasks like calling the OpenAI API are handled synchronously within the request-response cycle. For a production system, these would be moved to background tasks (e.g., using Celery) to avoid blocking the server.

-   **Basic UI/UX:** The frontend is functional and clean but prioritizes demonstrating the backend's capabilities over a highly polished design.

What You'd Build Next (If This Were Production-Ready)
-----------------------------------------------------

-   **Full Two-Way Calendar Sync:** The top priority would be to integrate with Google Calendar, Outlook, and other major providers. This would allow the assistant to see a user's complete schedule and add events directly to their primary calendar.

-   **Learning User Preferences:** The `UserPreferences` model is in place but not yet utilized. The next step would be for the agent to learn from user behavior. For example, if a user always sets a 60-minute reminder for "Sports" events, the assistant should start suggesting that automatically.

-   **Automated Rescheduling Agent:** Build on the conflict suggestion feature. If a high-priority event (like a "Doctor's Appointment") conflicts with a low-priority one (like a "Work Meeting"), the agent could automatically find a new time for the meeting and propose the change with a single click to approve.

-   **Multi-User and Communication Integration (MCP):**

    -   Allow events to be shared with other users of the application.

    -   Integrate with communication platforms like SMS (Twilio) or email (SendGrid). The "Share" feature would evolve into a true notification system, sending invites and reminders to family members' preferred devices.

-   **Location-Based Intelligence:** Integrate with mapping APIs (like Google Maps) to provide "time to leave" reminders based on real-time traffic conditions.