from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import time

from ..database import get_db
from ..models import Note
from ..schemas import NoteCreate, NoteResponse
from ..services.embedding_service import EmbeddingService
from ..services.vector_service import VectorService

router = APIRouter()

# Initialize services
embedding_service = EmbeddingService()
vector_service = VectorService()

@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(note_data: NoteCreate, db: Session = Depends(get_db)):
    """
    Create a new note with embedding and store in both PostgreSQL and Qdrant
    
    Args:
        note_data: The note data to create
        db: Database session
        
    Returns:
        The created note with metadata
    """
    try:
        # Generate embedding for the note content
        embedding = await embedding_service.get_embedding(note_data.content)
        
        # Store vector in Qdrant with metadata
        metadata = {
            "content": note_data.content,
            "title": note_data.title,
            "embedding_model": embedding_service.model
        }
        
        vector_id = await vector_service.store_vector(embedding, metadata)
        
        # Store note metadata in PostgreSQL
        db_note = Note(
            content=note_data.content,
            title=note_data.title,
            vector_id=vector_id,
            embedding_model=embedding_service.model
        )
        
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        
        return db_note
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create note: {str(e)}"
        )

@router.get("/notes", response_model=List[NoteResponse])
async def get_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all notes with pagination
    
    Args:
        skip: Number of notes to skip
        limit: Maximum number of notes to return
        db: Database session
        
    Returns:
        List of notes
    """
    notes = db.query(Note).offset(skip).limit(limit).all()
    return notes

@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """
    Get a specific note by ID
    
    Args:
        note_id: The ID of the note to retrieve
        db: Database session
        
    Returns:
        The requested note
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return note

@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """
    Delete a note and its associated vector
    
    Args:
        note_id: The ID of the note to delete
        db: Database session
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    try:
        # Delete vector from Qdrant
        await vector_service.delete_vector(note.vector_id)
        
        # Delete note from PostgreSQL
        db.delete(note)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete note: {str(e)}"
        )

@router.get("/notes/stats")
async def get_notes_stats(db: Session = Depends(get_db)):
    """
    Get statistics about notes and vectors
    
    Returns:
        Statistics about the system
    """
    try:
        # Get PostgreSQL stats
        total_notes = db.query(Note).count()
        
        # Get Qdrant stats
        collection_info = await vector_service.get_collection_info()
        
        return {
            "total_notes": total_notes,
            "vectors_count": collection_info["vectors_count"],
            "collection_status": collection_info["status"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        ) 