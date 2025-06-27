from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from .database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True)
    user_input = Column(Text)
    agent_response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    embedding_id = Column(String, nullable=True)  # Qdrant point ID

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    embedding_id = Column(String, nullable=True)  # Qdrant point ID
    metadata = Column(Text, nullable=True)  # JSON string for additional metadata 