"""
Intervention API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.user import User
from app.models.intervention import Intervention
from app.schemas.intervention import InterventionCreate, InterventionUpdate, InterventionResponse
from app.services.intervention_service import InterventionService

router = APIRouter()


def get_current_user(db: Session = Depends(get_db)) -> User:
    """Get current user - placeholder for auth implementation."""
    # TODO: Implement actual authentication
    # For now, return first user or create a test user
    user = db.query(User).first()
    if not user:
        user = User(email="test@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("", response_model=InterventionResponse, status_code=status.HTTP_201_CREATED)
async def create_intervention(
    intervention: InterventionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new intervention."""
    service = InterventionService(db)
    return await service.create_intervention(current_user.id, intervention)


@router.get("", response_model=List[InterventionResponse])
async def list_interventions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: str = None,
):
    """List all interventions for the current user."""
    service = InterventionService(db)
    return await service.list_interventions(current_user.id, status_filter)


@router.get("/{intervention_id}", response_model=InterventionResponse)
async def get_intervention(
    intervention_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific intervention."""
    service = InterventionService(db)
    intervention = await service.get_intervention(intervention_id, current_user.id)
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )
    return intervention


@router.patch("/{intervention_id}", response_model=InterventionResponse)
async def update_intervention(
    intervention_id: UUID,
    intervention_update: InterventionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an intervention."""
    service = InterventionService(db)
    intervention = await service.update_intervention(
        intervention_id, current_user.id, intervention_update
    )
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )
    return intervention


@router.delete("/{intervention_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_intervention(
    intervention_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an intervention."""
    service = InterventionService(db)
    success = await service.delete_intervention(intervention_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )
