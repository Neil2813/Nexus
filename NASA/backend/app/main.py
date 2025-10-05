"""Main FastAPI application for NASA Space Biology Knowledge Engine.

NEXUS: NASA Space Biology Knowledge Engine
A production-ready web platform for exploring NASA space biology data.
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings, logger, APP_NAME
from .nasa_client import NASAClient
from .ai_service import AIService
from .cache import CacheService
from .graph_service import GraphService
from .routes import router
import asyncio

# Global service instances
nasa_client: NASAClient = None
ai_service: AIService = None
cache_service: CacheService = None
graph_service: GraphService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info("Starting NEXUS: NASA Space Biology Knowledge Engine")
    
    global nasa_client, ai_service, cache_service, graph_service
    
    # Initialize services
    nasa_client = NASAClient()
    ai_service = AIService()
    cache_service = CacheService()
    graph_service = GraphService()
    
    # Initialize cache service
    await cache_service.init()
    logger.info("Cache service initialized")
    
    # Initialize graph service
    await graph_service.init()
    logger.info("Graph service initialized")
    
    # Store services in app state for access in routes
    app.state.nasa_client = nasa_client
    app.state.ai_service = ai_service
    app.state.cache_service = cache_service
    app.state.graph_service = graph_service
    
    logger.info("All services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NEXUS services...")
    
    try:
        await nasa_client.close()
        await ai_service.close()
        await graph_service.close()
        logger.info("All services closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    description="NASA Space Biology Knowledge Engine - Interactive platform for exploring space biology data",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.api_prefix)

@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "name": APP_NAME,
        "version": "1.0.0",
        "description": "NASA Space Biology Knowledge Engine API",
        "api_prefix": settings.api_prefix,
        "environment": settings.environment,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug
    )
