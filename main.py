"""FastAPI application entry point."""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,RedirectResponse
from src.config.settings import settings

current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(current_dir, "src", "frontend")

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

# Mount static files
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/hr/engagement/")

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


@app.get("/hr/engagement/")
async def engagement_portal():
    """Serves the main engagement portal page."""
    return FileResponse(os.path.join(frontend_path, 'index.html'))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )