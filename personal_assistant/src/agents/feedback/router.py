from fastapi import APIRouter, HTTPException
from src.models import FeedbackRequest, FeedbackResponse
from src.agents.feedback.service import feedback_agent

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for processing"""
    try:
        analysis, response_message = await feedback_agent.process(request.message)
        
        # In a real application, you would store the feedback in a database
        # if it's not spam
        
        return FeedbackResponse(
            success=not analysis.is_spam,
            message=response_message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}") 