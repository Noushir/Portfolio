"""
Direct fix for Groq client issue
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("direct_fix")

def get_groq_api_key():
    """Get the Groq API key from environment or secret file"""
    # Check if secret is mounted as a file (Cloud Run Secret Manager integration)
    secret_path = "/secrets/GROQ_API_KEY"
    if os.path.exists(secret_path):
        logger.info(f"Reading API key from secret file: {secret_path}")
        with open(secret_path, "r") as f:
            return f.read().strip()
    
    # Fallback to environment variable
    api_key = os.environ.get("GROQ_API_KEY")
    logger.info(f"API key available in env: {bool(api_key)}")
    return api_key

def test_groq_client():
    """Test initializing the Groq client"""
    try:
        # Try to import Groq
        logger.info("Importing Groq package...")
        import groq
        logger.info(f"Groq package version: {groq.__version__}")
        
        # Get API key
        api_key = get_groq_api_key()
        logger.info(f"API key available: {bool(api_key)}")
        
        # Initialize client with just the API key
        logger.info("Initializing Groq client with just api_key parameter...")
        client = groq.Groq(api_key=api_key)
        logger.info("Groq client initialized successfully!")
        
        # Test a simple completion
        logger.info("Testing chat completion...")
        messages = [{"role": "user", "content": "Hello, how are you?"}]
        completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
        )
        logger.info(f"Response: {completion.choices[0].message.content}")
        
        return True
    except Exception as e:
        import traceback
        logger.error(f"Error: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info(f"Python version: {sys.version}")
    success = test_groq_client()
    if success:
        logger.info("Test succeeded!")
    else:
        logger.error("Test failed!")
        sys.exit(1) 