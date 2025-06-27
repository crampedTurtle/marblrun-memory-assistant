from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class NoteCreate(BaseModel):
    """Schema for creating a new note"""
    content: str = Field(..., min_length=1, max_length=10000, description="Note content")
    title: Optional[str] = Field(None, max_length=255, description="Optional note title")

class NoteResponse(BaseModel):
    """Schema for note response"""
    id: int
    content: str
    title: Optional[str]
    vector_id: str
    embedding_model: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    """Schema for query request"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")

class QueryResponse(BaseModel):
    """Schema for query response"""
    query: str
    results: List[NoteResponse]
    total_found: int
    search_time_ms: float

class SearchResult(BaseModel):
    """Schema for search result with similarity score"""
    note: NoteResponse
    similarity_score: float 