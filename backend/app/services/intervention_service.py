"""
Intervention service for business logic.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date
from app.models.intervention import Intervention
from app.schemas.intervention import InterventionCreate, InterventionUpdate, InterventionResponse


class InterventionService:
    """Service for intervention operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_intervention(
        self, user_id: UUID, intervention_data: InterventionCreate
    ) -> InterventionResponse:
        """Create a new intervention."""
        intervention = Intervention(
            user_id=user_id,
            **intervention_data.model_dump()
        )
        self.db.add(intervention)
        self.db.commit()
        self.db.refresh(intervention)
        return InterventionResponse.model_validate(intervention)
    
    async def list_interventions(
        self, user_id: UUID, status_filter: Optional[str] = None
    ) -> List[InterventionResponse]:
        """List interventions for a user."""
        query = self.db.query(Intervention).filter(Intervention.user_id == user_id)
        
        if status_filter:
            query = query.filter(Intervention.status == status_filter)
        
        interventions = query.order_by(Intervention.start_date.desc()).all()
        return [InterventionResponse.model_validate(i) for i in interventions]
    
    async def get_intervention(
        self, intervention_id: UUID, user_id: UUID
    ) -> Optional[InterventionResponse]:
        """Get a specific intervention."""
        intervention = self.db.query(Intervention).filter(
            Intervention.id == intervention_id,
            Intervention.user_id == user_id
        ).first()
        
        if not intervention:
            return None
        
        return InterventionResponse.model_validate(intervention)
    
    async def update_intervention(
        self, intervention_id: UUID, user_id: UUID, update_data: InterventionUpdate
    ) -> Optional[InterventionResponse]:
        """Update an intervention."""
        intervention = self.db.query(Intervention).filter(
            Intervention.id == intervention_id,
            Intervention.user_id == user_id
        ).first()
        
        if not intervention:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(intervention, key, value)
        
        self.db.commit()
        self.db.refresh(intervention)
        return InterventionResponse.model_validate(intervention)
    
    async def delete_intervention(
        self, intervention_id: UUID, user_id: UUID
    ) -> bool:
        """Delete an intervention."""
        intervention = self.db.query(Intervention).filter(
            Intervention.id == intervention_id,
            Intervention.user_id == user_id
        ).first()
        
        if not intervention:
            return False
        
        self.db.delete(intervention)
        self.db.commit()
        return True
