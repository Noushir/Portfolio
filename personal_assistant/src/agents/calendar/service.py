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
    
    async def process(self, input_data):
        """Process calendar-related queries"""
        system_prompt = """You are a calendar assistant that helps schedule meetings.
        When asked about availability or booking, respond with information about how to use the calendar API.
        """
        
        messages = [{"role": "user", "content": input_data}]
        response = await self.generate_llm_response(messages, system_prompt)
        
        return response
    
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