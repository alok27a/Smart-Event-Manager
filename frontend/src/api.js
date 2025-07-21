export const api = {
  // Base URL for the backend API
  API_URL: 'http://127.0.0.1:8000/api/v1',

  // Function to handle user signup
  signUp: async (email, password) => {
    const response = await fetch(`${api.API_URL}/users/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Signup failed');
    }
    return response.json();
  },

  // Function to handle user login
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${api.API_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }
    return response.json();
  },

  // Function to get all events for the authenticated user
  getEvents: async (token) => {
    const response = await fetch(`${api.API_URL}/events`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error('Failed to fetch events');
    return response.json();
  },

  // Function to parse unstructured text and create/update an event
  parseEvent: async (text, token) => {
    const response = await fetch(`${api.API_URL}/events/parse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to parse event');
    }
    return response.json();
  },
  
  // Function to add a reminder to an event
  addReminder: async (eventId, reminder, token) => {
    const response = await fetch(`${api.API_URL}/events/${eventId}/reminders`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(reminder),
    });
    if (!response.ok) throw new Error('Failed to add reminder');
    return response.json();
  },

  // Function to update the status of an event
  updateEventStatus: async (eventId, statusUpdate, token) => {
    const response = await fetch(`${api.API_URL}/events/${eventId}/status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(statusUpdate),
    });
    if (!response.ok) throw new Error('Failed to update status');
    return response.json();
  },
  
  // Function to share an event
  shareEvent: async (eventId, shareWith, token) => {
    const response = await fetch(`${api.API_URL}/events/${eventId}/share`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ share_with: shareWith }),
    });
    if (!response.ok) throw new Error('Failed to share event');
    return response.json();
  },
  
  deleteEvent: async (eventId, token) => {
    const response = await fetch(`${api.API_URL}/events/${eventId}`, {
        method: 'DELETE',
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    if (response.status !== 204 && !response.ok) {
        throw new Error('Failed to delete event');
    }
    return;
  }

};
