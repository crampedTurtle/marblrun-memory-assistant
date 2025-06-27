from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from .database import Base

class Note(Base):
    """Database model for storing note metadata"""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    title = Column(String(255), nullable=True)
    vector_id = Column(String(255), unique=True, nullable=False)  # Qdrant point ID
    embedding_model = Column(String(100), default="text-embedding-ada-002")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}', vector_id='{self.vector_id}')>" 