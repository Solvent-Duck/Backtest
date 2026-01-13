"""
Analysis API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.intervention import Intervention
from app.schemas.analysis import AnalysisResultResponse, InterventionAnalysisResponse
from app.services.analysis_service import analyze_intervention

router = APIRouter()


@router.post("/interventions/{intervention_id}", response_model=InterventionAnalysisResponse)
async def run_analysis(
    intervention_id: UUID,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
):
    """Run analysis for an intervention"""
    intervention = await db.get(Intervention, intervention_id)
    
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    
    # TODO: Verify user owns this intervention
    
    # Run analysis
    results = await analyze_intervention(str(intervention_id), db)
    
    # Calculate summary
    significant_count = sum(1 for r in results if r.is_significant)
    total_count = len(results)
    
    summary = {
        "total_metrics_analyzed": total_count,
        "significant_changes": significant_count,
        "intervention_name": intervention.name,
        "intervention_start": intervention.start_date.isoformat(),
        "intervention_end": intervention.end_date.isoformat() if intervention.end_date else None,
    }
    
    return InterventionAnalysisResponse(
        intervention_id=intervention_id,
        results=[AnalysisResultResponse.model_validate(r) for r in results],
        summary=summary,
    )


@router.get("/interventions/{intervention_id}/results", response_model=List[AnalysisResultResponse])
async def get_analysis_results(
    intervention_id: UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
):
    """Get existing analysis results for an intervention"""
    intervention = await db.get(Intervention, intervention_id)
    
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    
    # TODO: Verify user owns this intervention
    
    from app.models.analysis_result import AnalysisResult
    from sqlalchemy import select
    
    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.intervention_id == intervention_id)
    )
    results = result.scalars().all()
    
    return results
