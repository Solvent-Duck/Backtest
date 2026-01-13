"""
Health data API endpoints.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.user import User
from app.schemas.data_import import DataImportResponse, DataImportStatus
from app.services.health_data_service import HealthDataService
from app.workers.health_data_worker import process_health_export
import asyncio

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


@router.post("/upload", response_model=DataImportResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_health_data(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload Apple Health XML export file."""
    if not file.filename.endswith(('.xml', '.zip')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be XML or ZIP format"
        )
    
    service = HealthDataService(db)
    import_record = await service.create_import_record(
        current_user.id, file.filename, file.size
    )
    
    # Store file temporarily
    file_path = await service.store_temp_file(file, import_record.id)
    
    # Process in background using Celery
    process_health_export.delay(
        file_path,
        str(import_record.id),
        str(current_user.id)
    )
    
    return import_record


@router.get("/imports", response_model=List[DataImportResponse])
async def list_imports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all data imports for the current user."""
    service = HealthDataService(db)
    return await service.list_imports(current_user.id)


@router.get("/imports/{import_id}", response_model=DataImportResponse)
async def get_import_status(
    import_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get status of a specific data import."""
    service = HealthDataService(db)
    import_record = await service.get_import(import_id, current_user.id)
    if not import_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import not found"
        )
    return import_record


@router.get("/metrics", response_model=List[dict])
async def get_metrics(
    metric_type: str = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get health metrics for the current user."""
    service = HealthDataService(db)
    return await service.get_metrics(
        current_user.id, metric_type, start_date, end_date
    )
