import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from src.agents.knowledge.router import router as knowledge_router
from src.agents.feedback.router import router as feedback_router
from src.agents.calendar.router import router as calendar_router

# Create FastAPI app
app = FastAPI(
    title="Agentic AI Assistant",
    description="Backend for an AI assistant with specialized agents",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(knowledge_router, prefix="/api", tags=["knowledge"])
app.include_router(feedback_router, prefix="/api", tags=["feedback"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Agentic AI Assistant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 