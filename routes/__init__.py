"""API routes module."""
from .health import router as health_router
from .math import router as math_router
from .educational import router as educational_router

__all__ = ["health_router", "math_router", "educational_router"]
