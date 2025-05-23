import json
import os
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from groq import Groq

# Import Google Calendar integration
from src.agents.calendar.google_calendar import GoogleCalendarManager
from src.utils.auth import create_oauth_flow, credentials_to_dict
# Import email sender for feedback notifications
from src.utils.email_sender import EmailSender
# Import feedback analyzer
from src.agents.feedback.feedback_agent import FeedbackAnalyzer

# Load environment variables from .env file if present
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
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
    event_link: Optional[str] = None

class FeedbackAnalysis(BaseModel):
    is_spam: bool
    sentiment: str
    priority: int
    category: Optional[str] = None

# Configuration


def get_groq_api_key():
    # Check if secret is mounted as a file (Cloud Run Secret Manager integration)
    secret_path = "/secrets/GROQ_API_KEY"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    # Fallback to environment variable
    return os.environ.get("GROQ_API_KEY")

GROQ_API_KEY = get_groq_api_key()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
PROFILE_PATH = os.getenv("PROFILE_PATH", "profile.json")

# Log configuration (without exposing the API key)
logger.info(f"Using model: {GROQ_MODEL}")
logger.info(f"Profile path: {PROFILE_PATH}")
logger.info(f"API key configured: {'Yes' if GROQ_API_KEY else 'No'}")

# Check if email configuration is complete
email_config = {
    "smtp_server": os.getenv("EMAIL_SMTP_SERVER"),
    "smtp_port": os.getenv("EMAIL_SMTP_PORT"),
    "username": os.getenv("EMAIL_USERNAME"),
    "password": os.getenv("EMAIL_PASSWORD"),
    "recipient": os.getenv("FEEDBACK_EMAIL_RECIPIENT")
}
if all(email_config.values()):
    logger.info("Email configuration is complete for feedback notifications")
else:
    logger.warning("Email configuration is incomplete. Feedback notifications will not be sent.")

# Monkey-patch the Groq client to handle the proxies parameter properly
def _patch_groq():
    import groq
    from groq._client import Groq as OriginalGroq
    
    logger.info("Monkey-patching Groq client to fix initialization issues")
    
    # Create a wrapper that strips out problematic parameters
    class PatchedGroq(OriginalGroq):
        def __init__(self, **kwargs):
            # Only pass the api_key parameter
            if 'api_key' in kwargs:
                super().__init__(api_key=kwargs['api_key'])
            else:
                super().__init__()
    
    # Replace the original class
    groq.Groq = PatchedGroq
    return True

# Apply the patch
_patch_groq()

# LLM Client
class GroqClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or GROQ_API_KEY
        self.model = model or GROQ_MODEL
        self.client = None
        
        # Only initialize at creation if API key exists
        if self.api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Groq client if API key is available"""
        try:
            import groq
            import sys
            logger.info(f"Python version: {sys.version}")
            logger.info(f"Groq package version: {groq.__version__}")
            logger.info(f"API key available: {bool(self.api_key)}")
            
            # CRITICAL: Create client with ONLY the API key
            if self.api_key:
                try:
                    # Directly use api_key parameter only
                    self.client = groq.Groq(api_key=self.api_key)
                    logger.info("Groq client initialized successfully")
                    return True
                except Exception as e:
                    logger.error(f"Failed to initialize Groq client: {e}")
            return False
        except Exception as e:
            logger.error(f"Error in _initialize_client: {e}")
            return False
    
    async def generate_response(self, messages, system_prompt=None):
        """Generate a response from the Groq API"""
        # Ensure client is initialized
        if not self.client:
            success = self._initialize_client()
            if not success:
                raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured or invalid")
        
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
        try:
            completion = self.client.chat.completions.create(
                messages=formatted_messages,
                model=self.model,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            raise HTTPException(status_code=500, detail=f"API error: {str(e)}")

# Base Agent
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

# Knowledge Agent
class KnowledgeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="KnowledgeAgent",
            description="Answers questions about Mohammed Noushir from profile data"
        )
        self.profile_data = self._load_profile()
        logger.info(f"KnowledgeAgent initialized with profile data: {self.profile_data.get('name', 'No name found')}")
    
    def _load_profile(self):
        """Load user profile from JSON file"""
        try:
            # First try to read from profile.json in the same directory
            profile_path = PROFILE_PATH
            logger.info(f"Attempting to load profile from: {profile_path}")
            
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as file:
                    logger.info(f"Profile file found at {profile_path}")
                    return json.load(file)
            
            # If that fails, try to find the file in the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            profile_path = os.path.join(current_dir, "profile.json")
            logger.info(f"Trying alternate profile path: {profile_path}")
            
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as file:
                    logger.info(f"Profile file found at {profile_path}")
                    return json.load(file)
            
            # If both fail, log the issue and return the hardcoded profile
            logger.warning(f"Profile file not found at {profile_path}, using hardcoded data")
            
            # Fallback to hardcoded profile data if file doesn't exist
            return {
                "name": "Mohammed Noushir",
                "bio": "AI/ML researcher, innovator, and builder with a passion for agentic AI, multimodal systems, and real-world impact.",
                "skills": [
                    {"name": "Python", "level": "Expert"},
                    {"name": "C", "level": "Intermediate"},
                    {"name": "PyTorch", "level": "Advanced"},
                    {"name": "TensorFlow", "level": "Advanced"},
                    {"name": "LangChain", "level": "Advanced"},
                    {"name": "Agentic AI", "level": "Advanced"},
                    {"name": "Knowledge Graphs", "level": "Advanced"},
                    {"name": "AWS", "level": "Advanced"},
                    {"name": "Docker", "level": "Intermediate"},
                    {"name": "Leadership", "level": "Soft Skill"}
                ]
            }
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            return {}
    
    async def process(self, query):
        """Process a knowledge query"""
        # Create system prompt with profile data
        system_prompt = f"""You are a helpful assistant representing Mohammed Noushir.
        Keep it short and concise but informative with a touch of humor sometimes. Keep a conversation tone like a real person
        Answer questions based on this profile information only,:
        {json.dumps(self.profile_data, indent=2)}
        
        If you don't know the answer, say so politely. 
        """
        
        # Generate response
        messages = [{"role": "user", "content": query}]
        response = await self.generate_llm_response(messages, system_prompt)
        
        return response

# Feedback Agent
class FeedbackAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FeedbackAgent",
            description="Processes and filters user feedback"
        )
        # Initialize feedback analyzer with email capabilities
        self.feedback_analyzer = FeedbackAnalyzer()
        
    async def process(self, feedback_message, rating=None, category=None):
        """Process feedback and determine if it's genuine
        
        Args:
            feedback_message: The feedback message text
            rating: Optional numerical rating
            category: Optional feedback category
            
        Returns:
            Tuple of (analysis, response_message)
        """
        try:
            # Use feedback analyzer to process feedback and send email
            feedback_data, response_message = await self.feedback_analyzer.analyze_feedback(
                feedback_message=feedback_message,
                llm_client=groq_client,
                rating=rating,
                category=category
            )
            
            # Create analysis result
            analysis = FeedbackAnalysis(
                is_spam=feedback_data.get("is_spam", False),
                sentiment=feedback_data.get("sentiment", "neutral"),
                priority=feedback_data.get("priority", 1),
                category=feedback_data.get("category", "other")
            )
            
            return analysis, response_message
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            return FeedbackAnalysis(is_spam=False, sentiment="neutral", priority=1, category="error"), f"Error processing feedback: {str(e)}"

# Calendar Agent
class CalendarAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CalendarAgent",
            description="Manages calendar availability and bookings"
        )
        # Initialize Google Calendar Manager
        self.calendar_manager = GoogleCalendarManager()
        
        # Use fallback demo slots if not authenticated with Google Calendar
        self.use_demo = not self.calendar_manager.is_authenticated()
        if self.use_demo:
            logger.warning("Using demo calendar slots as fallback (not authenticated with Google Calendar)")
            self.available_slots = self._generate_demo_slots()
        else:
            logger.info("Successfully connected to Google Calendar")
            self.available_slots = []
    
    def _generate_demo_slots(self):
        """Generate demo time slots for the next 7 days"""
        from datetime import datetime, timedelta
        
        slots = []
        start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        # If current time is past 9 AM, start from tomorrow
        if datetime.now().hour >= 9:
            start_date = start_date + timedelta(days=1)
        
        # Generate slots for 7 days, 9 AM to 5 PM, 1-hour slots
        for day in range(7):
            current_day = start_date + timedelta(days=day)
            for hour in range(9, 17):  # 9 AM to 5 PM
                slot_start = current_day.replace(hour=hour)
                slot_end = slot_start + timedelta(hours=1)
                slots.append({
                    "start": slot_start.isoformat(),
                    "end": slot_end.isoformat()
                })
        
        return slots
    
    async def process(self, input_data):
        """Process calendar-related queries"""
        try:
            system_prompt = """You are a calendar assistant for Mohammed Noushir.
            When responding to queries about booking appointments or availability, be helpful and professional.
            Mohammed Noushir is available for 1-hour meetings between 9 AM and 5 PM on weekdays.
            """
            
            messages = [{"role": "user", "content": input_data}]
            response = await self.generate_llm_response(messages, system_prompt)
            
            return response
        except Exception as e:
            logger.error(f"Error processing calendar request: {str(e)}")
            return f"Sorry, I couldn't process your calendar request: {str(e)}"
    
    async def get_availability(self, days=7):
        """Get available time slots for the next X days"""
        if not self.use_demo:
            # Use Google Calendar to get real availability
            try:
                logger.info("Getting availability from Google Calendar")
                return self.calendar_manager.get_available_slots(days=days)
            except Exception as e:
                logger.error(f"Error getting Google Calendar availability: {str(e)}")
                logger.info("Falling back to demo slots")
                self.use_demo = True
                return self._generate_demo_slots()
        else:
            # Use demo slots
            logger.info("Using demo availability slots")
            return self.available_slots
    
    async def book_slot(self, booking_request):
        """Book a time slot in the calendar"""
        try:
            # Extract booking details
            start_time = booking_request.start_time
            end_time = booking_request.end_time
            name = booking_request.name
            email = booking_request.email
            reason = booking_request.reason or f"Meeting with {name}"
            
            if not self.use_demo:
                # Use Google Calendar for real booking
                try:
                    logger.info(f"Booking with Google Calendar: {name} ({email}) for {start_time}")
                    
                    # Create event summary and description
                    summary = f"Meeting: {name}"
                    description = f"Meeting with {name} ({email})\n\nReason: {reason}"
                    
                    # Create the event
                    result = self.calendar_manager.create_event(
                        start_time=start_time,
                        end_time=end_time,
                        attendee_email=email,
                        summary=summary,
                        description=description
                    )
                    
                    if not result:
                        raise ValueError("Failed to create calendar event")
                    
                    return {
                        "booking_id": result["event_id"],
                        "name": name,
                        "email": email,
                        "start_time": start_time,
                        "end_time": end_time,
                        "reason": reason,
                        "link": result.get("link")
                    }
                except Exception as e:
                    logger.error(f"Error booking with Google Calendar: {str(e)}")
                    logger.info("Falling back to demo booking")
                    self.use_demo = True
                    # Continue with demo booking below
            
            # Demo booking (fallback if Google Calendar fails or not authenticated)
            if self.use_demo:
                # Simple validation - check if the slot exists in available slots
                slot_exists = any(
                    slot["start"] == start_time and slot["end"] == end_time
                    for slot in self.available_slots
                )
                
                if not slot_exists:
                    raise ValueError("The requested time slot is not available")
                
                # Create a booking reference
                import uuid
                booking_id = str(uuid.uuid4())[:8]
                
                # Remove the booked slot from available slots
                self.available_slots = [
                    slot for slot in self.available_slots
                    if not (slot["start"] == start_time and slot["end"] == end_time)
                ]
                
                return {
                    "booking_id": booking_id,
                    "name": name,
                    "email": email,
                    "start_time": start_time,
                    "end_time": end_time,
                    "reason": reason
                }
            
        except ValueError as e:
            logger.error(f"Invalid booking request: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Error booking appointment: {str(e)}")
            raise Exception(f"Could not book appointment: {str(e)}")

# Initialize agents
groq_client = GroqClient()
knowledge_agent = KnowledgeAgent()
feedback_agent = FeedbackAgent()
calendar_agent = CalendarAgent()

# Create FastAPI app
app = FastAPI(
    title="Agentic AI Assistant",
    description="Backend for an AI assistant with specialized agents",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Knowledge Agent routes
@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Process chat messages and route to knowledge agent"""
    try:
        logger.info(f"Received chat message: {message.content}")
        
        # Try to generate a response
        response = await knowledge_agent.process(message.content)
        logger.info(f"Generated response")
        return ChatResponse(content=response, agent=AgentType.KNOWLEDGE)
    except ValueError as e:
        # Special handling for configuration errors
        logger.error(f"Configuration error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"content": f"API configuration error: {str(e)}", "agent": AgentType.KNOWLEDGE}
        )
    except HTTPException as e:
        # Pass through HTTP exceptions with their status codes
        logger.error(f"HTTP error: {str(e.detail)}")
        return JSONResponse(
            status_code=e.status_code,
            content={"content": f"API error: {str(e.detail)}", "agent": AgentType.KNOWLEDGE}
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"content": f"Sorry, I encountered an error: {str(e)}", "agent": AgentType.KNOWLEDGE}
        )

# Feedback Agent routes
@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for processing"""
    try:
        analysis, response_message = await feedback_agent.process(
            feedback_message=request.message,
            rating=request.rating,
            category=request.category
        )
        
        return FeedbackResponse(
            success=not analysis.is_spam,
            message=response_message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")

# Calendar Agent routes
@app.get("/api/calendar/availability", response_model=AvailabilityResponse)
async def get_availability(days: int = 7):
    """Get calendar availability for the next X days"""
    try:
        logger.info(f"Getting availability for next {days} days")
        available_slots = await calendar_agent.get_availability(days)
        
        # Convert to TimeSlot objects
        time_slots = [TimeSlot(start=slot["start"], end=slot["end"]) for slot in available_slots]
        
        return AvailabilityResponse(available_slots=time_slots)
    except Exception as e:
        logger.error(f"Error getting availability: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calendar/book", response_model=BookingResponse)
async def book_slot(request: BookingRequest):
    """Book a calendar slot"""
    try:
        logger.info(f"Booking request: {request.name} ({request.email}) for {request.start_time} to {request.end_time}")
        
        booking_result = await calendar_agent.book_slot(request)
        
        # Log the booking success
        logger.info(f"Booking successful: {booking_result['booking_id']}")
        
        return BookingResponse(
            success=True,
            event_id=booking_result["booking_id"],
            message=f"Appointment successfully booked with {request.name} for {request.start_time}",
            event_link=booking_result.get("link")
        )
    except ValueError as e:
        # Return a 400 error for validation errors
        logger.error(f"Validation error in booking request: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": str(e)}
        )
    except Exception as e:
        logger.error(f"Error booking slot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Google Calendar Authentication routes
@app.get("/api/calendar/auth/url")
async def get_auth_url():
    """Get Google OAuth authorization URL"""
    try:
        flow = create_oauth_flow()
        auth_url, _ = flow.authorization_url(prompt="consent")
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Error generating auth URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendar/oauth/callback")
async def oauth_callback(code: str, state: str = None):
    """Handle OAuth callback from Google"""
    try:
        flow = create_oauth_flow()
        flow.fetch_token(code=code)
        
        # Get credentials and save them
        credentials = flow.credentials
        creds_dict = credentials_to_dict(credentials)
        
        # Save to GoogleCalendarManager
        calendar_agent.calendar_manager.save_credentials(creds_dict)
        
        # Update agent to use Google Calendar
        calendar_agent.use_demo = False
        
        logger.info("Successfully authenticated with Google Calendar")
        
        # Return success page
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Calendar Authentication Successful</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 40px; }
                .success { color: #4CAF50; font-size: 24px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1 class="success">Authentication Successful!</h1>
            <p>Your Google Calendar has been connected successfully.</p>
            <p>You can close this window and return to the application.</p>
        </body>
        </html>
        """
        
        return JSONResponse(
            content={"success": True, "message": "Authentication successful"},
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        logger.error(f"Error in OAuth callback: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Authentication failed: {str(e)}"}
        )

@app.get("/")
async def root():
    """Root endpoint with basic system information"""
    # Check if API key is available
    api_key_status = "Configured" if GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key" else "Not configured"
    
    # Return system information
    return {
        "message": "Welcome to the Agentic AI Assistant API",
        "version": "0.1.0",
        "status": "running",
        "api_key_status": api_key_status,
        "model": GROQ_MODEL,
        "env_vars": list(os.environ.keys()),  # Show available environment variables (names only for security)
        "endpoints": [
            {"path": "/api/chat", "method": "POST", "description": "Chat with the knowledge agent"},
            {"path": "/api/feedback", "method": "POST", "description": "Submit feedback"},
            {"path": "/api/calendar/availability", "method": "GET", "description": "Get calendar availability"},
            {"path": "/api/calendar/book", "method": "POST", "description": "Book a calendar slot"},
            {"path": "/", "method": "GET", "description": "This information"}
        ]
    }

# Entry point for GCP (Google Cloud Run/App Engine)
if __name__ == "__main__":
    import uvicorn
    print("Starting Agentic AI Assistant API on http://0.0.0.0:8000")
    logger.info("Starting Agentic AI Assistant API on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000))) 