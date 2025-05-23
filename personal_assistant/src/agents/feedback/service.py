from src.agents.base import BaseAgent
from pydantic import BaseModel
from typing import Optional

class FeedbackAnalysis(BaseModel):
    is_spam: bool
    sentiment: str
    priority: int
    category: Optional[str] = None

class FeedbackAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FeedbackAgent",
            description="Processes and filters user feedback"
        )
        # Keywords for simple filtering
        self.spam_keywords = ["spam", "virus", "hack", "free money", "lottery"]
        
    async def process(self, feedback_message):
        """Process feedback and determine if it's genuine"""
        # Simple keyword-based spam detection
        is_spam = any(keyword in feedback_message.lower() for keyword in self.spam_keywords)
        
        # Use LLM for sentiment analysis and categorization
        system_prompt = """Analyze the following feedback message. 
        Determine:
        1. The sentiment (positive, negative, neutral)
        2. A priority level (1-5, where 5 is highest)
        3. A category (bug, feature request, complaint, praise, question, other)
        
        Format your response as JSON with fields: sentiment, priority, category
        """
        
        messages = [{"role": "user", "content": feedback_message}]
        llm_analysis = await self.generate_llm_response(messages, system_prompt)
        
        # Parse LLM response
        try:
            import json
            analysis_dict = json.loads(llm_analysis)
            sentiment = analysis_dict.get("sentiment", "neutral")
            priority = analysis_dict.get("priority", 1)
            category = analysis_dict.get("category", "other")
        except:
            sentiment = "neutral"
            priority = 1
            category = "other"
        
        # Create analysis result
        analysis = FeedbackAnalysis(
            is_spam=is_spam,
            sentiment=sentiment,
            priority=priority,
            category=category
        )
        
        # Return analysis and a response message
        response_message = "Thank you for your feedback!" if not is_spam else "Your message has been flagged as potential spam."
        
        return analysis, response_message

# Create singleton instance
feedback_agent = FeedbackAgent() 