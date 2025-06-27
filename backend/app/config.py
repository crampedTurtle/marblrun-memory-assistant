import os
from typing import Optional

class Settings:
    """Application settings and configuration"""
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres.home.lan:5432/marblrun")
    
    # Qdrant settings
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "memories")
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "text-embedding-ada-002"
    OPENAI_CHAT_MODEL: str = "gpt-3.5-turbo"
    
    # Vector settings
    VECTOR_SIZE: int = 1536  # OpenAI ada-002 embedding size
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Application settings
    MAX_CONTENT_LENGTH: int = 10000  # Maximum note length
    MAX_SEARCH_RESULTS: int = 10

# Global settings instance
settings = Settings() 