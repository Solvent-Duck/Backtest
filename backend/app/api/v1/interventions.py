"""
Intervention API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.intervention import Intervention
from app.schemas.intervention import (
    InterventionCreate,
    InterventionUpdate,
    InterventionResponse,
)

router = APIRouter()


@router.post("", response_model=InterventionResponse, status_code=201)
async def create_intervention(
    intervention: InterventionCreate,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
    # current_user: User = Depends(get_current_user),
):
    """Create a new intervention"""
    # TODO: Get user_id from authenticated user
    user_id = UUID("00000000-0000-0000-0000-000000000000")  # Placeholder
    
    new_intervention = Intervention(
        user_id=user_id,
        **intervention.model_dump(),
    )
    
    db.add(new_intervention)
    await db.commit()
    await db.refresh(new_intervention)
    
    return new_intervention


@router.get("", response_model=List[InterventionResponse])
async def list_interventions(
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
):
    """List all interventions for the current user"""
    # TODO: Get user_id from authenticated user
    user_id = UUID("00000000-0000-0000-0000-000000000000")  # Placeholder
    
    result = await db.execute(
        select(Intervention).where(Intervention.user_id == user_id).order_by(Intervention.start_date.desc())
    )
    interventions = result.scalars().all()
    
    return interventions


@router.get("/{intervention_id}", response_model=InterventionResponse)
async def get_intervention(
    intervention_id: UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
):
    """Get a specific intervention"""
    intervention = await db.get(Intervention, intervention_id)
    
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    
    # TODO: Verify user owns this intervention
    
    return intervention


@router.patch("/{intervention_id}", response_model=InterventionResponse)
async def update_intervention(
    intervention_id: UUID,
    intervention_update: InterventionUpdate,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
):
    """Update an intervention"""
    intervention = await db.get(Intervention, intervention_id)
    
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    
    # TODO: Verify user owns this intervention
    
    # Update fields
    update_data = intervention_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(intervention, field, value)
    
    await db.commit()
    await db.refresh(intervention)
    
    return intervention


@router.delete("/{intervention_id}", status_code=204)
async def delete_intervention(
    intervention_id: UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
):
    """Delete an intervention"""
    intervention = await db.get(Intervention, intervention_id)
    
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    
    # TODO: Verify user owns this intervention
    
    await db.delete(intervention)
    await db.commit()
    
    return None
