"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import connection, query, schema
from app.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Determine frontend path (works both locally and in Docker)
FRONTEND_PATH = Path(__file__).parent.parent.parent / "frontend"
if not FRONTEND_PATH.exists():
    # Docker path
    FRONTEND_PATH = Path("/app/frontend")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests with real client IP."""
    
    async def dispatch(self, request: Request, call_next):
        # Get real client IP (supports X-Forwarded-For from Azure Load Balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Get other useful info
        user_agent = request.headers.get("User-Agent", "unknown")[:100]
        
        # Process request
        response = await call_next(request)
        
        # Log access (skip health checks for cleaner logs)
        if request.url.path != "/health":
            logger.info(
                f"IP: {client_ip} | {request.method} {request.url.path} | "
                f"Status: {response.status_code} | UA: {user_agent}"
            )
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Universal SQL-RAG Interface - Ask questions in natural language, get SQL answers",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS - allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add access logging middleware (must be after CORS)
app.add_middleware(AccessLogMiddleware)

# Include routers
app.include_router(connection.router, prefix=settings.api_prefix, tags=["Connection"])
app.include_router(schema.router, prefix=settings.api_prefix, tags=["Schema"])
app.include_router(query.router, prefix=settings.api_prefix, tags=["Query"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/")
async def root():
    """Serve the frontend HTML page."""
    index_file = FRONTEND_PATH / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
