from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import time

from ..database import get_db
from ..models import Note
from ..schemas import QueryRequest, QueryResponse, SearchResult
from ..services.search_service import SearchService

router = APIRouter()

# Initialize search service
search_service = SearchService()

@router.post("/search/semantic", response_model=QueryResponse)
async def semantic_search(
    query_data: QueryRequest, 
    score_threshold: Optional[float] = Query(None, description="Minimum similarity score"),
    db: Session = Depends(get_db)
):
    """
    Perform semantic search using embeddings
    
    Args:
        query_data: The search query
        score_threshold: Minimum similarity score threshold
        db: Database session
        
    Returns:
        Semantic search results
    """
    try:
        # Perform semantic search
        search_results = await search_service.semantic_search(
            query_data.query,
            limit=query_data.limit,
            score_threshold=score_threshold
        )
        
        # Get full note data from PostgreSQL for each result
        results = []
        for result in search_results['results']:
            note = db.query(Note).filter(Note.vector_id == result['id']).first()
            if note:
                results.append(SearchResult(
                    note=note,
                    similarity_score=result['score']
                ))
        
        return QueryResponse(
            query=search_results['query'],
            results=[result.note for result in results],
            total_found=len(results),
            search_time_ms=search_results['search_time_ms']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )

@router.post("/search/hybrid")
async def hybrid_search(
    query_data: QueryRequest,
    semantic_weight: float = Query(0.7, ge=0.0, le=1.0, description="Weight for semantic similarity"),
    text_weight: float = Query(0.3, ge=0.0, le=1.0, description="Weight for text similarity"),
    db: Session = Depends(get_db)
):
    """
    Perform hybrid search combining semantic and text similarity
    
    Args:
        query_data: The search query
        semantic_weight: Weight for semantic similarity (0-1)
        text_weight: Weight for text similarity (0-1)
        db: Database session
        
    Returns:
        Hybrid search results
    """
    try:
        # Validate weights
        if abs(semantic_weight + text_weight - 1.0) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Semantic and text weights must sum to 1.0"
            )
        
        # Perform hybrid search
        search_results = await search_service.hybrid_search(
            query_data.query,
            limit=query_data.limit,
            semantic_weight=semantic_weight,
            text_weight=text_weight
        )
        
        # Get full note data from PostgreSQL for each result
        results = []
        for result in search_results['results']:
            note = db.query(Note).filter(Note.vector_id == result['id']).first()
            if note:
                results.append({
                    'note': note,
                    'combined_score': result['score'],
                    'semantic_score': result['semantic_score'],
                    'text_score': result['text_score']
                })
        
        return {
            'query': search_results['query'],
            'results': results,
            'total_found': len(results),
            'search_time_ms': search_results['search_time_ms'],
            'search_type': search_results['search_type'],
            'weights': search_results['weights']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hybrid search failed: {str(e)}"
        )

@router.post("/search/batch")
async def batch_search(
    queries: List[str],
    limit: int = Query(5, ge=1, le=20, description="Maximum results per query"),
    db: Session = Depends(get_db)
):
    """
    Perform batch search for multiple queries
    
    Args:
        queries: List of search queries
        limit: Maximum results per query
        db: Database session
        
    Returns:
        Batch search results
    """
    try:
        if len(queries) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 queries allowed per batch"
            )
        
        # Perform batch search
        search_results = await search_service.batch_search(queries, limit)
        
        # Get full note data for each result
        formatted_results = []
        for query_result in search_results:
            notes = []
            for result in query_result['results']:
                note = db.query(Note).filter(Note.vector_id == result['id']).first()
                if note:
                    notes.append(SearchResult(
                        note=note,
                        similarity_score=result['score']
                    ))
            
            formatted_results.append({
                'query': query_result['query'],
                'results': [result.note for result in notes],
                'total_found': len(notes),
                'query_index': query_result['query_index']
            })
        
        return {
            'batch_results': formatted_results,
            'total_queries': len(queries)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch search failed: {str(e)}"
        )

@router.post("/search/filtered")
async def filtered_search(
    query: str,
    filters: Dict[str, Any],
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Search with advanced filtering options
    
    Args:
        query: Search query
        filters: Filter conditions (e.g., date ranges, tags, etc.)
        limit: Maximum number of results
        db: Database session
        
    Returns:
        Filtered search results
    """
    try:
        # Perform filtered search
        search_results = await search_service.search_with_filters(
            query, filters, limit
        )
        
        # Get full note data from PostgreSQL for each result
        results = []
        for result in search_results['results']:
            note = db.query(Note).filter(Note.vector_id == result['id']).first()
            if note:
                results.append(SearchResult(
                    note=note,
                    similarity_score=result['score']
                ))
        
        return {
            'query': search_results['query'],
            'results': [result.note for result in results],
            'total_found': len(results),
            'filters_applied': search_results['filters_applied']
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Filtered search failed: {str(e)}"
        )

@router.get("/search/similar/{note_id}")
async def find_similar_notes(
    note_id: str,
    limit: int = Query(5, ge=1, le=20, description="Maximum number of similar notes"),
    db: Session = Depends(get_db)
):
    """
    Find notes similar to a specific note
    
    Args:
        note_id: ID of the reference note
        limit: Maximum number of similar notes
        db: Database session
        
    Returns:
        Similar notes with similarity scores
    """
    try:
        # Find similar notes
        similar_results = await search_service.get_similar_notes(note_id, limit)
        
        # Get full note data from PostgreSQL
        similar_notes = []
        for result in similar_results['similar_notes']:
            note = db.query(Note).filter(Note.vector_id == result['id']).first()
            if note:
                similar_notes.append(SearchResult(
                    note=note,
                    similarity_score=result['score']
                ))
        
        # Get reference note
        reference_note = db.query(Note).filter(Note.vector_id == note_id).first()
        
        return {
            'reference_note': reference_note,
            'similar_notes': [result.note for result in similar_notes],
            'total_found': len(similar_notes)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar notes: {str(e)}"
        )

@router.get("/search/suggestions")
async def get_search_suggestions(
    partial_query: str = Query(..., description="Partial search query"),
    limit: int = Query(5, ge=1, le=10, description="Maximum number of suggestions")
):
    """
    Get search suggestions based on partial query
    
    Args:
        partial_query: Partial search query
        limit: Maximum number of suggestions
        
    Returns:
        List of suggested search terms
    """
    try:
        suggestions = await search_service.get_search_suggestions(partial_query, limit)
        return {
            'partial_query': partial_query,
            'suggestions': suggestions
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search suggestions: {str(e)}"
        )

@router.get("/search/analytics")
async def get_search_analytics():
    """
    Get analytics about search performance and patterns
    
    Returns:
        Search analytics data
    """
    try:
        analytics = await search_service.get_search_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search analytics: {str(e)}"
        ) 