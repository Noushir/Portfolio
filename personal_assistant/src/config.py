import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Helper function to get the API key from GCP Secret Manager or environment
def get_groq_api_key():
    # Check if secret is mounted as a file (Cloud Run Secret Manager integration)
    secret_path = "/secrets/GROQ_API_KEY"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    # Fallback to environment variable
    return os.environ.get("GROQ_API_KEY")

# LLM Configuration
GROQ_API_KEY = get_groq_api_key()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

# Google Calendar API
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/calendar/oauth/callback")
GOOGLE_AUTH_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# Email Configuration
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_SMTP_PORT = os.getenv("EMAIL_SMTP_PORT", "587")
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FEEDBACK_EMAIL_RECIPIENT = os.getenv("FEEDBACK_EMAIL_RECIPIENT")

# Application Settings
PROFILE_PATH = os.getenv("PROFILE_PATH", "profile.json")
CALENDAR_TOKEN_PATH = os.getenv("CALENDAR_TOKEN_PATH", "data/calendar_token.json") 