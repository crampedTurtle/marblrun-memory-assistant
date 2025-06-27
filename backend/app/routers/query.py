from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import time

from ..database import get_db
from ..models import Note
from ..schemas import QueryRequest, QueryResponse, SearchResult
from ..services.embedding_service import EmbeddingService
from ..services.vector_service import VectorService

router = APIRouter()

# Initialize services
embedding_service = EmbeddingService()
vector_service = VectorService()

@router.post("/query", response_model=QueryResponse)
async def search_memory(query_data: QueryRequest, db: Session = Depends(get_db)):
    """
    Search memory using semantic similarity
    
    Args:
        query_data: The search query
        db: Database session
        
    Returns:
        Search results with similarity scores
    """
    start_time = time.time()
    
    try:
        # Generate embedding for the query
        query_embedding = await embedding_service.get_embedding(query_data.query)
        
        # Search for similar vectors in Qdrant
        search_results = await vector_service.search_vectors(
            query_embedding,
            limit=query_data.limit
        )
        
        # Get full note data from PostgreSQL for each result
        results = []
        for result in search_results:
            note = db.query(Note).filter(Note.vector_id == result['id']).first()
            if note:
                results.append(SearchResult(
                    note=note,
                    similarity_score=result['score']
                ))
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return QueryResponse(
            query=query_data.query,
            results=[result.note for result in results],
            total_found=len(results),
            search_time_ms=search_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/query/similar/{note_id}")
async def find_similar_notes(note_id: int, limit: int = 5, db: Session = Depends(get_db)):
    """
    Find notes similar to a specific note
    
    Args:
        note_id: The ID of the note to find similar ones for
        limit: Maximum number of similar notes to return
        db: Database session
        
    Returns:
        List of similar notes with similarity scores
    """
    # Get the target note
    target_note = db.query(Note).filter(Note.id == note_id).first()
    if not target_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    try:
        # Get the embedding for the target note content
        target_embedding = await embedding_service.get_embedding(target_note.content)
        
        # Search for similar vectors, excluding the target note itself
        search_results = await vector_service.search_vectors(
            target_embedding,
            limit=limit + 1  # Get one extra to account for the target note
        )
        
        # Filter out the target note and get full note data
        results = []
        for result in search_results:
            if result['id'] != target_note.vector_id:
                note = db.query(Note).filter(Note.vector_id == result['id']).first()
                if note:
                    results.append(SearchResult(
                        note=note,
                        similarity_score=result['score']
                    ))
        
        return {
            "target_note": target_note,
            "similar_notes": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar notes: {str(e)}"
        )

@router.get("/query/suggestions")
async def get_search_suggestions(db: Session = Depends(get_db)):
    """
    Get search suggestions based on recent notes
    
    Returns:
        List of suggested search terms
    """
    try:
        # Get recent notes to suggest search terms
        recent_notes = db.query(Note).order_by(Note.created_at.desc()).limit(10).all()
        
        suggestions = []
        for note in recent_notes:
            if note.title:
                suggestions.append(note.title)
            else:
                # Extract first few words from content as suggestion
                words = note.content.split()[:5]
                suggestions.append(" ".join(words) + "...")
        
        return {
            "suggestions": suggestions[:5]  # Return top 5 suggestions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        ) 