import json
import logging
import asyncio
from src.utils.email_sender import EmailSender

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackAnalyzer:
    """Analyzes and processes user feedback"""
    
    def __init__(self):
        # Keywords for simple filtering
        self.spam_keywords = ["spam", "virus", "hack", "free money", "lottery"]
        # Initialize email sender
        self.email_sender = EmailSender()
        
    async def analyze_feedback(self, feedback_message, llm_client, rating=None, category=None):
        """Analyze feedback message and send email notification if not spam
        
        Args:
            feedback_message: The feedback message text
            llm_client: LLM client for sentiment analysis
            rating: Optional user rating (1-5)
            category: Optional feedback category
            
        Returns:
            Tuple of (analysis_dict, response_message)
        """
        try:
            # Simple keyword-based spam detection
            is_spam = any(keyword in feedback_message.lower() for keyword in self.spam_keywords)
            
            if is_spam:
                logger.info("Feedback flagged as potential spam")
                return {
                    "is_spam": True,
                    "sentiment": "neutral",
                    "priority": 1,
                    "category": "spam"
                }, "Your message has been flagged as potential spam."
            
            # Use LLM for sentiment analysis and categorization
            system_prompt = """Analyze the following feedback message. 
            Determine:
            1. The sentiment (positive, negative, neutral)
            2. A priority level (1-5, where 5 is highest)
            3. A category (bug, feature request, complaint, praise, question, other)
            
            Format your response as JSON with fields: sentiment, priority, category
            """
            
            messages = [{"role": "user", "content": feedback_message}]
            llm_analysis = await llm_client.generate_response(messages, system_prompt)
            
            # Parse LLM response
            try:
                analysis_dict = json.loads(llm_analysis)
                sentiment = analysis_dict.get("sentiment", "neutral")
                priority = analysis_dict.get("priority", 1)
                llm_category = analysis_dict.get("category", "other")
            except:
                sentiment = "neutral"
                priority = 1
                llm_category = "other"
            
            # Create complete feedback data
            feedback_data = {
                "is_spam": False,
                "sentiment": sentiment,
                "priority": priority,
                "category": category or llm_category,
                "message": feedback_message,
                "rating": rating
            }
            
            # Send email notification asynchronously (don't wait for it to complete)
            asyncio.create_task(self.send_email_notification(feedback_data))
            
            # Return immediately with success message
            response_message = "Thank you for your feedback! I've sent it to Mohammed."
            
            return feedback_data, response_message
            
        except Exception as e:
            logger.error(f"Error analyzing feedback: {str(e)}")
            return {
                "is_spam": False, 
                "sentiment": "neutral", 
                "priority": 1, 
                "category": "error"
            }, f"Error processing feedback: {str(e)}"
    
    async def send_email_notification(self, feedback_data):
        """Send feedback notification email
        
        Args:
            feedback_data: Dictionary with feedback analysis
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            result = self.email_sender.send_feedback_notification(feedback_data)
            if result:
                logger.info(f"Email notification sent successfully for feedback: {feedback_data.get('category')}")
            else:
                logger.warning(f"Failed to send email notification for feedback: {feedback_data.get('category')}")
            return result
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False 