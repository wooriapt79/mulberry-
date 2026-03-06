"""
Mulberry Phase 1+ - API Module
"""

from app.api.routes import router as core_router
from app.api.routes_extended import router as extended_router

__all__ = ["core_router", "extended_router"]
