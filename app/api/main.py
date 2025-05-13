import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.api.llm_service import get_llm_engine
from app.api.vector_db import get_vector_db
from app.api.rag_pipeline import RAGPipeline
from app.api.documents import router as documents_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    use_rag: bool = True
    temperature: float = 0.7
    max_tokens: int = 1024

class ChatResponse(BaseModel):
    response: str
    retrieved_documents: Optional[List[Dict[str, Any]]] = None

# Dependency to get vector DB from app state
async def get_vector_db_dependency():
    return app.state.vector_db

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the LLM model and vector DB
    logger.info("Starting up the application...")
    app.state.llm_engine = await get_llm_engine()
    app.state.vector_db = await get_vector_db()
    app.state.rag_pipeline = RAGPipeline(app.state.llm_engine, app.state.vector_db)
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("Shutting down the application...")
    if hasattr(app.state, "llm_engine"):
        await app.state.llm_engine.shutdown()
    if hasattr(app.state, "vector_db"):
        await app.state.vector_db.shutdown()
    logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="API for a RAG-enhanced chatbot using Mistral-7B",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(documents_router, tags=["documents"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info(f"Received chat request with {len(request.messages)} messages")
        
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Get the last user message
        user_message = next((msg.content for msg in reversed(request.messages) 
                            if msg.role.lower() == "user"), None)
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Process with RAG pipeline
        if request.use_rag:
            response, retrieved_docs = await app.state.rag_pipeline.generate_response(
                user_message, 
                request.temperature,
                request.max_tokens
            )
            return ChatResponse(
                response=response,
                retrieved_documents=retrieved_docs
            )
        else:
            # Direct LLM response without RAG
            response = await app.state.llm_engine.generate(
                user_message,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            return ChatResponse(response=response)
            
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Override the dependency in the documents router
app.dependency_overrides[lambda: None] = get_vector_db_dependency

if __name__ == "__main__":
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True) 