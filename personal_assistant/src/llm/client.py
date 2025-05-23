import os
import logging
from groq import Groq
from src.config import GROQ_API_KEY, GROQ_MODEL

# Configure logging
logger = logging.getLogger(__name__)

# We assume that app.py has already patched the Groq client
class GroqClient:
    def __init__(self, api_key=None, model=None):
        api_key = api_key or GROQ_API_KEY
        
        # Debug logging
        logger.info(f"Initializing GroqClient in src/llm/client.py")
        logger.info(f"API key available: {bool(api_key)}")
        
        try:
            # The Groq client should be already patched
            self.client = Groq(api_key=api_key)
            logger.info("Groq client initialized successfully in src/llm/client.py")
        except Exception as e:
            logger.error(f"Error initializing Groq client in src/llm/client.py: {e}")
            raise e
            
        # Use the model from config or a hardcoded default
        self.model = model or GROQ_MODEL or "llama3-8b-8192"

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
        try:
            completion = self.client.chat.completions.create(
                messages=formatted_messages,
                model=self.model,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            raise e

# Create a singleton instance
groq_client = GroqClient() 