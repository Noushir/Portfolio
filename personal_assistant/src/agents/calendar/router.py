from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
import json
from src.agents.calendar.service import calendar_agent
from src.models import AvailabilityResponse, BookingRequest, BookingResponse
from src.utils.auth import create_oauth_flow, credentials_to_dict

router = APIRouter()

@router.get("/oauth/start")
async def start_oauth():
    """Start the OAuth flow for Google Calendar"""
    flow = create_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return {"authorization_url": authorization_url}

@router.get("/oauth/callback")
async def oauth_callback(request: Request):
    """Handle OAuth callback from Google"""
    try:
        # Get the authorization code from the request
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Missing authorization code")
        
        # Complete the OAuth flow
        flow = create_oauth_flow()
        flow.fetch_token(code=code)
        
        # Get credentials and save them
        credentials = flow.credentials
        credentials_dict = credentials_to_dict(credentials)
        
        # Save credentials to file
        calendar_agent._save_credentials(credentials_dict)
        
        return {"message": "Successfully authenticated with Google Calendar"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth error: {str(e)}")

@router.get("/availability", response_model=AvailabilityResponse)
async def get_availability(days: int = 7):
    """Get available time slots for the next X days"""
    try:
        available_slots = await calendar_agent.get_availability(days)
        return AvailabilityResponse(available_slots=available_slots)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/book", response_model=BookingResponse)
async def book_slot(booking_request: BookingRequest):
    """Book a time slot in the calendar"""
    try:
        event_id = await calendar_agent.book_slot(booking_request)
        return BookingResponse(
            success=True,
            event_id=event_id,
            message="Appointment successfully booked"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 