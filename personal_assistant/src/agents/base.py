import json
import os
from abc import ABC, abstractmethod
from src.llm.client import groq_client

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def process(self, input_data):
        """Process input data and return a response"""
        pass
    
    async def generate_llm_response(self, messages, system_prompt=None):
        """Generate a response using the LLM"""
        return await groq_client.generate_response(messages, system_prompt) 