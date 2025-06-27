from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import notes, query, search
from app.database import engine
from app.models import Base
from app.utils import get_system_health, initialize_database

# Initialize database and collections
initialize_database()

# Initialize FastAPI app
app = FastAPI(
    title="MarblRun Memory Assistant",
    description="A local memory assistant with vector search capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(search.router, prefix="/api", tags=["advanced-search"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "MarblRun Memory Assistant API", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "marblrun-backend",
        "version": "1.0.0"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Comprehensive system health check"""
    return await get_system_health() 