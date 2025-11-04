"""Main FastAPI application for Wolfram Math Service."""
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config.settings import settings
from routes import math_router, educational_router, health_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Wolfram Math Service", 
                host=settings.server_host, 
                port=settings.server_port)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Wolfram Math Service")


# Create FastAPI app
app = FastAPI(
    title="Wolfram Math & Science Service",
    description="Advanced math and science problem-solving using Wolfram Alpha and GPT-5",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(math_router, prefix="/api/v1/math", tags=["math"])
app.include_router(educational_router, prefix="/api/v1/educational", tags=["educational"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Wolfram Math & Science Service",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "math": "/api/v1/math",
            "educational": "/api/v1/educational",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
