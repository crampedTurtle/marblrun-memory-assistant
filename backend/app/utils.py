import asyncio
from typing import Dict, Any
from sqlalchemy.orm import Session
from .database import SessionLocal
from .services.vector_service import VectorService
from .services.embedding_service import EmbeddingService

async def check_database_health() -> Dict[str, Any]:
    """Check database connectivity and health"""
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

async def check_qdrant_health() -> Dict[str, Any]:
    """Check Qdrant connectivity and health"""
    try:
        vector_service = VectorService()
        info = await vector_service.get_collection_info()
        return {"status": "healthy", "qdrant": info}
    except Exception as e:
        return {"status": "unhealthy", "qdrant": str(e)}

async def check_openai_health() -> Dict[str, Any]:
    """Check OpenAI API connectivity"""
    try:
        embedding_service = EmbeddingService()
        # Test with a simple embedding
        test_embedding = await embedding_service.get_embedding("test")
        return {"status": "healthy", "openai": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "openai": str(e)}

async def get_system_health() -> Dict[str, Any]:
    """Get comprehensive system health status"""
    db_health = await check_database_health()
    qdrant_health = await check_qdrant_health()
    openai_health = await check_openai_health()
    
    overall_status = "healthy"
    if any(check["status"] == "unhealthy" for check in [db_health, qdrant_health, openai_health]):
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "database": db_health,
            "qdrant": qdrant_health,
            "openai": openai_health
        }
    }

def initialize_database():
    """Initialize database tables and collections"""
    try:
        from .database import engine
        from .models import Base
        from .services.vector_service import VectorService
        
        # Create database tables
        Base.metadata.create_all(bind=engine)
        
        # Initialize vector service (creates collection if needed)
        vector_service = VectorService()
        
        return True
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False 