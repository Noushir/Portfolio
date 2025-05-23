#!/usr/bin/env python3

# Create .env.template file with necessary environment variables

env_content = '''# LLM Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-8b-8192

# Google Calendar OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth/callback

# Email Configuration
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
FEEDBACK_EMAIL_RECIPIENT=your_email@gmail.com

# Application Settings
PROFILE_PATH=profile.json
CALENDAR_TOKEN_PATH=data/calendar_token.json
'''

with open('.env.template', 'w') as f:
    f.write(env_content)

print(".env.template created successfully!") 