"""
Analysis API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.models.user import User
from app.schemas.analysis import InterventionAnalysisResponse
from app.services.analysis_service import AnalysisService

router = APIRouter()


def get_current_user(db: Session = Depends(get_db)) -> User:
    """Get current user - placeholder for auth implementation."""
    # TODO: Implement actual authentication
    user = db.query(User).first()
    if not user:
        user = User(email="test@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("/interventions/{intervention_id}/analyze", response_model=InterventionAnalysisResponse)
async def analyze_intervention(
    intervention_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run analysis for an intervention."""
    service = AnalysisService(db)
    result = await service.analyze_intervention(intervention_id, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found or insufficient data"
        )
    return result


@router.get("/interventions/{intervention_id}/results", response_model=InterventionAnalysisResponse)
async def get_intervention_results(
    intervention_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get existing analysis results for an intervention."""
    service = AnalysisService(db)
    result = await service.get_intervention_results(intervention_id, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found or no results available"
        )
    return result
