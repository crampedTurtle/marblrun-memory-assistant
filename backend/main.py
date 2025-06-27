from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import agents
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Assistant Platform",
    description="A platform for AI-powered assistants with memory and task execution",
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
app.include_router(agents.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "AI Assistant Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 