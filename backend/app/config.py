import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres.home.lan:5432/ai_assistants")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    
    # Agent settings
    AGENT_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Vector search settings
    VECTOR_SIZE: int = 1536  # OpenAI ada-002 embedding size
    SIMILARITY_THRESHOLD: float = 0.7

settings = Settings() 