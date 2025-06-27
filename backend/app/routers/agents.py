from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from ..database import get_db
from ..models import Conversation, Note
from ..schemas import ChatRequest, ChatResponse, NoteRequest, NoteResponse, SearchRequest, SearchResponse, SearchResult
from ..agents import Cara, Penny, Eva

router = APIRouter()

# Agent instances
agents = {
    "cara": Cara(),
    "penny": Penny(),
    "eva": Eva()
}

@router.post("/agent/{agent_name}/chat", response_model=ChatResponse)
async def chat_with_agent(
    agent_name: str,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with a specific AI agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    agent = agents[agent_name]
    
    # Generate response
    response = agent.generate_response(request.message, request.context)
    
    # Store conversation in database
    conversation = Conversation(
        agent_name=agent_name,
        user_input=request.message,
        agent_response=response
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    # Store in agent's memory
    embedding_id = agent.store_memory(
        f"User: {request.message}\nAgent: {response}",
        {"conversation_id": conversation.id}
    )
    
    # Update conversation with embedding ID
    conversation.embedding_id = embedding_id
    db.commit()
    
    return ChatResponse(
        response=response,
        agent_name=agent_name,
        conversation_id=conversation.id
    )

@router.post("/agent/{agent_name}/note", response_model=NoteResponse)
async def store_note(
    agent_name: str,
    request: NoteRequest,
    db: Session = Depends(get_db)
):
    """Store a note in agent's memory"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    agent = agents[agent_name]
    
    # Store note in database
    note = Note(
        agent_name=agent_name,
        content=request.content,
        metadata=json.dumps(request.metadata) if request.metadata else None
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    
    # Store in agent's memory
    embedding_id = agent.store_memory(
        request.content,
        {"note_id": note.id, "metadata": request.metadata}
    )
    
    # Update note with embedding ID
    note.embedding_id = embedding_id
    db.commit()
    
    return NoteResponse(
        id=note.id,
        content=note.content,
        agent_name=note.agent_name,
        created_at=note.created_at
    )

@router.get("/agent/{agent_name}/search", response_model=SearchResponse)
async def search_agent_memory(
    agent_name: str,
    q: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Search agent's memory for relevant information"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    agent = agents[agent_name]
    
    # Search in agent's memory
    memory_results = agent.search_memory(q, limit)
    
    # Convert to SearchResult format
    results = []
    for memory in memory_results:
        # Try to find corresponding conversation or note
        conversation = db.query(Conversation).filter(
            Conversation.embedding_id == memory.get("metadata", {}).get("conversation_id")
        ).first()
        
        note = db.query(Note).filter(
            Note.embedding_id == memory.get("metadata", {}).get("note_id")
        ).first()
        
        if conversation:
            results.append(SearchResult(
                content=memory["text"],
                score=memory["score"],
                source="conversation",
                created_at=conversation.created_at
            ))
        elif note:
            results.append(SearchResult(
                content=memory["text"],
                score=memory["score"],
                source="note",
                created_at=note.created_at
            ))
        else:
            # Fallback for orphaned memories
            results.append(SearchResult(
                content=memory["text"],
                score=memory["score"],
                source="memory",
                created_at=note.created_at if note else conversation.created_at
            ))
    
    return SearchResponse(
        results=results,
        query=q,
        agent_name=agent_name
    )

@router.get("/agents")
async def list_agents():
    """List all available agents"""
    return {
        "agents": [
            {
                "name": name,
                "display_name": agent.name,
                "description": agent._get_default_prompt()[:200] + "..."
            }
            for name, agent in agents.items()
        ]
    } 