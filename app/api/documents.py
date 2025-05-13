from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Models
class Document(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = {}

class DocumentBatch(BaseModel):
    documents: List[Document]

class DocumentResponse(BaseModel):
    success: bool
    count: int
    message: str

# Router
router = APIRouter()

@router.post("/documents", response_model=DocumentResponse)
async def add_documents(
    batch: DocumentBatch,
    vector_db=Depends(lambda: None)  # This will be injected by FastAPI from app state
):
    """
    Add documents to the vector database.
    """
    try:
        # Get the vector DB service from app state
        if not vector_db:
            raise HTTPException(status_code=500, detail="Vector database not initialized")
        
        # Convert Pydantic models to dictionaries
        docs = [doc.dict() for doc in batch.documents]
        
        # Add documents to vector database
        await vector_db.add_documents(docs)
        
        return DocumentResponse(
            success=True,
            count=len(docs),
            message=f"Successfully added {len(docs)} documents to vector database"
        )
        
    except Exception as e:
        logger.error(f"Error adding documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error adding documents: {str(e)}")

@router.get("/documents/count")
async def get_document_count(
    vector_db=Depends(lambda: None)
):
    """
    Get the number of documents in the vector database.
    """
    try:
        # Get the vector DB service from app state
        if not vector_db:
            raise HTTPException(status_code=500, detail="Vector database not initialized")
        
        # Get count from collection
        count = vector_db.collection.count()
        
        return {"count": count}
        
    except Exception as e:
        logger.error(f"Error getting document count: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting document count: {str(e)}")

@router.delete("/documents")
async def delete_all_documents(
    vector_db=Depends(lambda: None)
):
    """
    Delete all documents from the vector database.
    """
    try:
        # Get the vector DB service from app state
        if not vector_db:
            raise HTTPException(status_code=500, detail="Vector database not initialized")
        
        # Delete all documents
        vector_db.collection.delete(where={})
        
        return {"success": True, "message": "All documents deleted"}
        
    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}") 