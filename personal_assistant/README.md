# Agentic AI Assistant for Mohammed Noushir's Portfolio

This directory contains the backend implementation for the AI assistant featured in the portfolio website. The assistant can answer questions about Mohammed's background, process feedback, and manage calendar bookings.

## Architecture Overview

The backend is built with FastAPI and uses Groq's API for LLM inference. The system features three specialized agents:

1. **Knowledge Agent**: Answers questions based on profile data
2. **Feedback Agent**: Processes and filters user feedback
3. **Calendar Agent**: Manages calendar availability and bookings via Google Calendar API

## Project Structure

```
personal_assistant/
├── .env                      # Environment variables
├── Dockerfile                # Container configuration
├── requirements.txt          # Dependencies
├── main.py                   # Application entry point
├── src/
│   ├── config.py             # Global configuration
│   ├── models.py             # Shared models
│   ├── agents/
│   │   ├── base.py           # Base agent class
│   │   ├── knowledge/        # Knowledge agent implementation
│   │   ├── feedback/         # Feedback agent implementation
│   │   └── calendar/         # Calendar agent implementation
│   ├── llm/
│   │   └── client.py         # Groq API client
│   └── utils/
│       └── auth.py           # OAuth utilities
└── tests/                    # Test directory
```

## Implementation Details

### Environment Setup

Create a `.env` file with the following configuration:

```
# LLM Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama4_maverick

# Google Calendar API
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth/callback

# Application Settings
PROFILE_PATH=../src/data/profile.json
```

### Main Application

```python
# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from src.agents.knowledge.router import router as knowledge_router
from src.agents.feedback.router import router as feedback_router
from src.agents.calendar.router import router as calendar_router

# Create FastAPI app
app = FastAPI(
    title="Agentic AI Assistant",
    description="Backend for an AI assistant with specialized agents",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(knowledge_router, prefix="/api", tags=["knowledge"])
app.include_router(feedback_router, prefix="/api", tags=["feedback"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Agentic AI Assistant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### Core Models and Configuration

```python
# src/models.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class AgentType(str, Enum):
    KNOWLEDGE = "knowledge"
    FEEDBACK = "feedback"
    CALENDAR = "calendar"

class ChatMessage(BaseModel):
    content: str
    role: str = "user"

class ChatResponse(BaseModel):
    content: str
    agent: AgentType

class FeedbackRequest(BaseModel):
    message: str
    rating: Optional[int] = None
    category: Optional[str] = None

class FeedbackResponse(BaseModel):
    success: bool
    message: str

class TimeSlot(BaseModel):
    start: str  # ISO format
    end: str    # ISO format

class AvailabilityResponse(BaseModel):
    available_slots: List[TimeSlot]

class BookingRequest(BaseModel):
    start_time: str  # ISO format
    end_time: str    # ISO format
    name: str
    email: str
    reason: str

class BookingResponse(BaseModel):
    success: bool
    event_id: Optional[str] = None
    message: str
```

```python
# src/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

# Google Calendar API
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_AUTH_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# Application Settings
PROFILE_PATH = os.getenv("PROFILE_PATH", "../src/data/profile.json")
```

### Groq LLM Client

```python
# src/llm/client.py
import os
from groq import Groq
from src.config import GROQ_API_KEY, GROQ_MODEL

class GroqClient:
    def __init__(self, api_key=None, model=None):
        self.client = Groq(
            api_key=api_key or GROQ_API_KEY,
        )
        self.model = model or GROQ_MODEL

    async def generate_response(self, messages, system_prompt=None):
        """Generate a response from the Groq API"""
        formatted_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        # Add user messages
        for message in messages:
            formatted_messages.append({
                "role": message.get("role", "user"),
                "content": message.get("content", "")
            })
        
        # Call Groq API
        completion = self.client.chat.completions.create(
            messages=formatted_messages,
            model=self.model,
        )
        
        return completion.choices[0].message.content

# Create a singleton instance
groq_client = GroqClient()
```

### Base Agent Class

```python
# src/agents/base.py
import json
import os
from abc import ABC, abstractmethod
from src.llm.client import groq_client

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def process(self, input_data):
        """Process input data and return a response"""
        pass
    
    async def generate_llm_response(self, messages, system_prompt=None):
        """Generate a response using the LLM"""
        return await groq_client.generate_response(messages, system_prompt)
```

## Agent Implementations

### Knowledge Agent

```python
# src/agents/knowledge/service.py
import json
import os
from src.agents.base import BaseAgent
from src.config import PROFILE_PATH

class KnowledgeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="KnowledgeAgent",
            description="Answers questions about Mohammed Noushir from profile data"
        )
        self.profile_data = self._load_profile()
    
    def _load_profile(self):
        """Load user profile from JSON file"""
        try:
            with open(PROFILE_PATH, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading profile: {e}")
            return {}
    
    async def process(self, query):
        """Process a knowledge query"""
        # Create system prompt with profile data
        system_prompt = f"""You are a helpful assistant representing Mohammed Noushir.
        Answer questions based on this profile information only:
        {json.dumps(self.profile_data, indent=2)}
        
        If you don't know the answer, say so politely.
        """
        
        # Generate response
        messages = [{"role": "user", "content": query}]
        response = await self.generate_llm_response(messages, system_prompt)
        
        return response

# Create singleton instance
knowledge_agent = KnowledgeAgent()
```

```python
# src/agents/knowledge/router.py
from fastapi import APIRouter, HTTPException
from src.models import ChatMessage, ChatResponse, AgentType
from src.agents.knowledge.service import knowledge_agent

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Process chat messages and route to knowledge agent"""
    try:
        response = await knowledge_agent.process(message.content)
        return ChatResponse(content=response, agent=AgentType.KNOWLEDGE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
```

### Feedback Agent

```python
# src/agents/feedback/service.py
from src.agents.base import BaseAgent
from pydantic import BaseModel
from typing import Optional

class FeedbackAnalysis(BaseModel):
    is_spam: bool
    sentiment: str
    priority: int
    category: Optional[str] = None

class FeedbackAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FeedbackAgent",
            description="Processes and filters user feedback"
        )
        # Keywords for simple filtering
        self.spam_keywords = ["spam", "virus", "hack", "free money", "lottery"]
        
    async def process(self, feedback_message):
        """Process feedback and determine if it's genuine"""
        # Simple keyword-based spam detection
        is_spam = any(keyword in feedback_message.lower() for keyword in self.spam_keywords)
        
        # Use LLM for sentiment analysis and categorization
        system_prompt = """Analyze the following feedback message. 
        Determine:
        1. The sentiment (positive, negative, neutral)
        2. A priority level (1-5, where 5 is highest)
        3. A category (bug, feature request, complaint, praise, question, other)
        
        Format your response as JSON with fields: sentiment, priority, category
        """
        
        messages = [{"role": "user", "content": feedback_message}]
        llm_analysis = await self.generate_llm_response(messages, system_prompt)
        
        # Parse LLM response
        try:
            import json
            analysis_dict = json.loads(llm_analysis)
            sentiment = analysis_dict.get("sentiment", "neutral")
            priority = analysis_dict.get("priority", 1)
            category = analysis_dict.get("category", "other")
        except:
            sentiment = "neutral"
            priority = 1
            category = "other"
        
        # Create analysis result
        analysis = FeedbackAnalysis(
            is_spam=is_spam,
            sentiment=sentiment,
            priority=priority,
            category=category
        )
        
        # Return analysis and a response message
        response_message = "Thank you for your feedback!" if not is_spam else "Your message has been flagged as potential spam."
        
        return analysis, response_message

# Create singleton instance
feedback_agent = FeedbackAgent()
```

```python
# src/agents/feedback/router.py
from fastapi import APIRouter, HTTPException
from src.models import FeedbackRequest, FeedbackResponse
from src.agents.feedback.service import feedback_agent

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for processing"""
    try:
        analysis, response_message = await feedback_agent.process(request.message)
        
        # In a real application, you would store the feedback in a database
        # if it's not spam
        
        return FeedbackResponse(
            success=not analysis.is_spam,
            message=response_message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")
```

### Calendar Agent

```python
# src/agents/calendar/service.py
import os
import json
from datetime import datetime, timedelta
import pytz
from googleapiclient.errors import HttpError
from src.agents.base import BaseAgent
from src.utils.auth import dict_to_credentials, build_calendar_service
from src.models import TimeSlot

class CalendarAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CalendarAgent",
            description="Manages calendar availability and bookings"
        )
        self.token_path = "data/calendar_token.json"
        self.credentials = self._load_credentials()
        
    def _load_credentials(self):
        """Load Google Calendar credentials from file"""
        try:
            if os.path.exists(self.token_path):
                with open(self.token_path, 'r') as file:
                    return dict_to_credentials(json.load(file))
            return None
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None
    
    def _save_credentials(self, credentials_dict):
        """Save Google Calendar credentials to file"""
        os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
        with open(self.token_path, 'w') as file:
            json.dump(credentials_dict, file)
    
    async def get_availability(self, days=7):
        """Get available time slots for the next X days"""
        if not self.credentials:
            raise Exception("Calendar not authenticated. Please connect your Google Calendar.")
        
        try:
            # Build the calendar service
            service = build_calendar_service(self.credentials)
            
            # Calculate time range
            now = datetime.utcnow()
            end_date = now + timedelta(days=days)
            
            # Get busy periods from primary calendar
            body = {
                "timeMin": now.isoformat() + "Z",
                "timeMax": end_date.isoformat() + "Z",
                "items": [{"id": "primary"}]
            }
            
            events_result = service.freebusy().query(body=body).execute()
            busy_periods = events_result["calendars"]["primary"]["busy"]
            
            # Generate available slots (9 AM to 5 PM, 1-hour slots)
            available_slots = []
            current_date = now.replace(hour=9, minute=0, second=0, microsecond=0)
            
            # If we're past 9 AM, start from the next hour
            if now.hour >= 9:
                current_date = current_date.replace(hour=now.hour + 1)
            
            while current_date < end_date:
                # Only consider 9 AM to 5 PM
                if 9 <= current_date.hour < 17:
                    slot_end = current_date + timedelta(hours=1)
                    
                    # Check if slot overlaps with any busy period
                    is_available = True
                    for busy in busy_periods:
                        busy_start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
                        busy_end = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))
                        
                        if (current_date < busy_end and slot_end > busy_start):
                            is_available = False
                            break
                    
                    if is_available:
                        available_slots.append(
                            TimeSlot(
                                start=current_date.isoformat(),
                                end=slot_end.isoformat()
                            )
                        )
                
                # Move to next hour
                current_date += timedelta(hours=1)
            
            return available_slots
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise Exception(f"Calendar API error: {error}")
    
    async def book_slot(self, booking_request):
        """Book a time slot in the calendar"""
        if not self.credentials:
            raise Exception("Calendar not authenticated. Please connect your Google Calendar.")
        
        try:
            # Build the calendar service
            service = build_calendar_service(self.credentials)
            
            # Create event
            event = {
                'summary': f"Meeting with {booking_request.name}",
                'description': booking_request.reason,
                'start': {
                    'dateTime': booking_request.start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': booking_request.end_time,
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': booking_request.email},
                ],
                'reminders': {
                    'useDefault': True,
                },
            }
            
            event = service.events().insert(calendarId='primary', body=event).execute()
            return event.get('id')
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise Exception(f"Calendar API error: {error}")

# Create singleton instance
calendar_agent = CalendarAgent()
```

## Frontend Integration

To integrate this backend with the existing `ChatAssistant.jsx` component:

1. Update the handleSend function to call the backend API:

```jsx
const handleSend = async (e) => {
  e.preventDefault();
  if (!input.trim()) return;
  
  // Add user message to chat
  setMessages([...messages, { from: 'user', text: input }]);
  
  try {
    // Call the backend API
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: input }),
    });
    
    const data = await response.json();
    
    // Add assistant response to chat
    setMessages(msgs => [...msgs, { from: 'assistant', text: data.content }]);
  } catch (error) {
    console.error('Error calling API:', error);
    setMessages(msgs => [...msgs, 
      { from: 'assistant', text: 'Sorry, I encountered an error. Please try again later.' }
    ]);
  }
  
  setInput('');
};
```

## Deployment Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

### 3. Docker Deployment

```bash
docker build -t agentic-assistant .
docker run -p 8000:8000 agentic-assistant
```

## Next Steps

1. Add database integration for storing chat history
2. Implement authentication for the API
3. Add more sophisticated agent routing based on query intent
4. Expand the knowledge base with additional profile information
5. Add support for multi-turn conversations with context retention 

# API Key Setup

To use the AI Assistant, you need to set up a Groq API key:

1. Sign up for a Groq account at [groq.com](https://console.groq.com/signup)
2. Create an API key in your Groq account dashboard
3. Set the API key in your environment:

```bash
# For Windows
set GROQ_API_KEY=your_api_key_here

# For Linux/Mac
export GROQ_API_KEY=your_api_key_here
```

Or create a `.env` file in the `personal_assistant` directory with the following content:

```
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama3-8b-8192
PROFILE_PATH=profile.json
``` 