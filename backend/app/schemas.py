from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_name: str
    conversation_id: int

class NoteRequest(BaseModel):
    content: str
    metadata: Optional[dict] = None

class NoteResponse(BaseModel):
    id: int
    content: str
    agent_name: str
    created_at: datetime

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class SearchResult(BaseModel):
    content: str
    score: float
    source: str  # "conversation" or "note"
    created_at: datetime

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    agent_name: str 