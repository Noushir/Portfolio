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