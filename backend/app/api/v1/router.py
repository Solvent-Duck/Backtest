"""
Main API router for v1.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import interventions, health_data, analysis

api_router = APIRouter()

api_router.include_router(interventions.router, prefix="/interventions", tags=["interventions"])
api_router.include_router(health_data.router, prefix="/health-data", tags=["health-data"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
