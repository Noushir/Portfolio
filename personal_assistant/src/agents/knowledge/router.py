from fastapi import APIRouter, HTTPException
from src.models import ChatMessage, ChatResponse, AgentType
from src.agents.knowledge.service import knowledge_agent

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Process chat messages and route to knowledge agent"""
    try:
        response = await knowledge_agent.process(message.content)
        return ChatResponse(content=response, agent=AgentType.KNOWLEDGE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}") 