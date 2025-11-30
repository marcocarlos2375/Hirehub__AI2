"""
FastAPI routers for the HireHubAI Backend.
"""

from app.routers.parsing import router as parsing_router
from app.routers.health import router as health_router
from app.routers.scoring import router as scoring_router

__all__ = [
    'parsing_router',
    'health_router',
    'scoring_router',
]
