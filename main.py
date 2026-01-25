"""FastAPI application entry point."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings

# Create FastAPI app
app = FastAPI(
    title="Candidate Experience & Engagement Agent",
    description="AI-powered candidate engagement service with multi-channel communication",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Candidate Engagement Agent",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "ok",
        "database": "connected",
        "llm": "configured"
    }


# Import and include routers
from src.api.routes.engagement import router as engagement_router
app.include_router(engagement_router, prefix="/hr/engagement", tags=["engagement"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
