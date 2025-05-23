import os
import json
import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from googleapiclient.errors import HttpError
import logging

from src.utils.auth import dict_to_credentials, build_calendar_service
from src.config import CALENDAR_TOKEN_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleCalendarManager:
    """Manager for Google Calendar operations"""
    
    def __init__(self, token_path=None):
        self.token_path = token_path or CALENDAR_TOKEN_PATH
        self.service = None
        self.calendar_id = 'primary'  # Use primary calendar by default
        
        # Try to load saved credentials
        self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from saved token file"""
        try:
            if os.path.exists(self.token_path):
                with open(self.token_path, 'r') as token_file:
                    credentials_dict = json.load(token_file)
                    credentials = dict_to_credentials(credentials_dict)
                    self.service = build_calendar_service(credentials)
                    logger.info("Successfully loaded Google Calendar credentials")
                    return True
            else:
                logger.warning(f"No token file found at {self.token_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return False
    
    def save_credentials(self, credentials_dict):
        """Save credentials to token file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            
            with open(self.token_path, 'w') as token_file:
                json.dump(credentials_dict, token_file)
            
            # Reload credentials into service
            credentials = dict_to_credentials(credentials_dict)
            self.service = build_calendar_service(credentials)
            logger.info("Successfully saved Google Calendar credentials")
            return True
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            return False
    
    def is_authenticated(self):
        """Check if we have valid credentials"""
        return self.service is not None
    
    def get_available_slots(self, days=7, duration_minutes=60, working_hours=(9, 17)):
        """Get available time slots for the next X days
        
        Args:
            days: Number of days to look ahead
            duration_minutes: Duration of each meeting in minutes
            working_hours: Tuple of (start_hour, end_hour) in 24h format
        
        Returns:
            List of available time slots as dicts with start/end times
        """
        if not self.is_authenticated():
            logger.error("Not authenticated with Google Calendar")
            return []
        
        try:
            # Calculate time range
            now = datetime.datetime.utcnow()
            end_date = now + datetime.timedelta(days=days)
            
            # Get busy periods from calendar
            body = {
                "timeMin": now.isoformat() + "Z",
                "timeMax": end_date.isoformat() + "Z",
                "items": [{"id": self.calendar_id}]
            }
            
            events_result = self.service.freebusy().query(body=body).execute()
            busy_periods = events_result["calendars"][self.calendar_id]["busy"]
            
            # Generate all possible slots
            all_slots = []
            slot_duration = datetime.timedelta(minutes=duration_minutes)
            current_date = now.replace(hour=working_hours[0], minute=0, second=0, microsecond=0)
            
            # If current time is past the start of working hours, start from next slot
            if now.hour > working_hours[0] or (now.hour == working_hours[0] and now.minute > 0):
                # Round up to the next hour
                current_date = now.replace(second=0, microsecond=0)
                if now.minute > 0:
                    current_date += datetime.timedelta(hours=1)
                    current_date = current_date.replace(minute=0)
            
            # If it's past working hours, start tomorrow
            if current_date.hour >= working_hours[1]:
                current_date += datetime.timedelta(days=1)
                current_date = current_date.replace(hour=working_hours[0], minute=0)
            
            # Generate slots for all days
            end_datetime = now + datetime.timedelta(days=days)
            while current_date < end_datetime:
                # Only consider slots during working hours on weekdays (0=Monday, 6=Sunday)
                if current_date.weekday() < 5 and working_hours[0] <= current_date.hour < working_hours[1]:
                    slot_end = current_date + slot_duration
                    all_slots.append({
                        "start": current_date.isoformat(),
                        "end": slot_end.isoformat()
                    })
                
                # Move to next slot
                current_date += slot_duration
                
                # If we've moved past working hours, jump to the next day
                if current_date.hour >= working_hours[1]:
                    current_date += datetime.timedelta(days=1)
                    current_date = current_date.replace(hour=working_hours[0], minute=0)
            
            # Filter out busy slots
            available_slots = []
            for slot in all_slots:
                slot_start = parse(slot["start"])
                slot_end = parse(slot["end"])
                
                is_available = True
                for busy in busy_periods:
                    busy_start = parse(busy["start"])
                    busy_end = parse(busy["end"])
                    
                    # Check if there's any overlap
                    if (slot_start < busy_end and slot_end > busy_start):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(slot)
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error getting available slots: {str(e)}")
            return []
    
    def create_event(self, start_time, end_time, attendee_email, summary, description=""):
        """Create a calendar event
        
        Args:
            start_time: ISO format start time
            end_time: ISO format end time
            attendee_email: Email of the attendee
            summary: Event title/summary
            description: Event description
            
        Returns:
            Dictionary with event details including event_id on success
            None on failure
        """
        if not self.is_authenticated():
            logger.error("Not authenticated with Google Calendar")
            return None
        
        try:
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': attendee_email},
                ],
                'reminders': {
                    'useDefault': True,
                },
            }
            
            event = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event, 
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Event created: {event.get('htmlLink')}")
            
            return {
                'event_id': event.get('id'),
                'link': event.get('htmlLink'),
                'summary': event.get('summary'),
                'start_time': start_time,
                'end_time': end_time,
                'attendee': attendee_email
            }
            
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            return None
            
    def get_event(self, event_id):
        """Get details of a specific event"""
        if not self.is_authenticated():
            logger.error("Not authenticated with Google Calendar")
            return None
            
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            return event
        except Exception as e:
            logger.error(f"Error getting event {event_id}: {str(e)}")
            return None
    
    def cancel_event(self, event_id):
        """Cancel a calendar event"""
        if not self.is_authenticated():
            logger.error("Not authenticated with Google Calendar")
            return False
            
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Event {event_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling event {event_id}: {str(e)}")
            return False 