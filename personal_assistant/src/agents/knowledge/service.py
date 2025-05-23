import json
import os
from src.agents.base import BaseAgent
from src.config import PROFILE_PATH

class KnowledgeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="KnowledgeAgent",
            description="Answers questions about Mohammed Noushir from profile data"
        )
        self.profile_data = self._load_profile()
    
    def _load_profile(self):
        """Load user profile from JSON file"""
        try:
            with open(PROFILE_PATH, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading profile: {e}")
            return {}
    
    async def process(self, query):
        """Process a knowledge query"""
        # Create system prompt with profile data
        system_prompt = f"""You are a helpful assistant representing Mohammed Noushir.
        Answer questions based on this profile information only:
        {json.dumps(self.profile_data, indent=2)}
        
        If you don't know the answer, say so politely.
        """
        
        # Generate response
        messages = [{"role": "user", "content": query}]
        response = await self.generate_llm_response(messages, system_prompt)
        
        return response

# Create singleton instance
knowledge_agent = KnowledgeAgent() 