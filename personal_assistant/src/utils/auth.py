import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from src.config import (
    GOOGLE_CLIENT_ID, 
    GOOGLE_CLIENT_SECRET, 
    GOOGLE_REDIRECT_URI,
    GOOGLE_AUTH_SCOPES
)

def create_oauth_flow():
    """Create a Google OAuth2 flow"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=GOOGLE_AUTH_SCOPES
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    return flow

def credentials_to_dict(credentials):
    """Convert Google credentials to a dictionary"""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'expiry': credentials.expiry.isoformat() if credentials.expiry else None
    }

def dict_to_credentials(credentials_dict):
    """Convert a dictionary to Google credentials"""
    return Credentials(
        token=credentials_dict['token'],
        refresh_token=credentials_dict['refresh_token'],
        token_uri=credentials_dict['token_uri'],
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret'],
        scopes=credentials_dict['scopes']
    )

def build_calendar_service(credentials):
    """Build a Google Calendar service from credentials"""
    service = build('calendar', 'v3', credentials=credentials)
    return service 