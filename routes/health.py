"""Health check routes."""
from fastapi import APIRouter, status
from datetime import datetime
import psutil
import os

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "wolfram-math-service"
    }


@router.get("/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check():
    """Detailed health check with system metrics."""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "wolfram-math-service",
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": disk.percent
                }
            },
            "process": {
                "pid": os.getpid(),
                "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
            }
        }
    except Exception as e:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "wolfram-math-service",
            "error": f"Could not retrieve system metrics: {str(e)}"
        }
