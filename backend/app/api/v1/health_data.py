"""
Health data API endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
import os
import aiofiles
from datetime import date

from app.core.database import get_db
from app.core.config import settings
from app.models.data_import import DataImport
from app.models.health_metric import HealthMetric
from app.schemas.data_import import DataImportResponse, DataImportStatusResponse
from app.schemas.health_metric import DailyMetricResponse
from app.services.health_data_service import process_health_export

router = APIRouter()


@router.post("/upload", response_model=DataImportResponse, status_code=201)
async def upload_health_data(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
):
    """Upload Apple Health export file"""
    
    # Validate file type
    if not (file.filename.endswith(".xml") or file.filename.endswith(".zip")):
        raise HTTPException(status_code=400, detail="File must be .xml or .zip")
    
    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content) / (1024 * 1024)  # MB
    
    if file_size > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE_MB}MB",
        )
    
    # TODO: Get user_id from authenticated user
    user_id = UUID("00000000-0000-0000-0000-000000000000")  # Placeholder
    
    # Create import record
    import_record = DataImport(
        user_id=user_id,
        filename=file.filename,
        file_size_mb=file_size,
        status="pending",
    )
    
    db.add(import_record)
    await db.commit()
    await db.refresh(import_record)
    
    # Save file temporarily
    os.makedirs(settings.TEMP_STORAGE_PATH, exist_ok=True)
    file_path = os.path.join(settings.TEMP_STORAGE_PATH, f"{import_record.id}.zip")
    
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    # Process in background
    # Note: For production, use Celery task instead of BackgroundTasks
    # For now, we'll process synchronously in background task
    background_tasks.add_task(
        process_health_export_async,
        file_path,
        str(user_id),
        str(import_record.id),
    )
    
    return import_record


async def process_health_export_async(
    file_path: str,
    user_id: str,
    import_id: str,
):
    """Async wrapper for background processing"""
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            await process_health_export(file_path, user_id, import_id, db)
        except Exception as e:
            print(f"Error processing health export: {e}")
            # Update import record with error
            import_record = await db.get(DataImport, import_id)
            if import_record:
                import_record.status = "failed"
                import_record.error_message = str(e)
                await db.commit()
        finally:
            # Clean up file
            if os.path.exists(file_path):
                os.remove(file_path)


@router.get("/imports", response_model=List[DataImportResponse])
async def list_imports(
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
):
    """List all data imports for the current user"""
    # TODO: Get user_id from authenticated user
    user_id = UUID("00000000-0000-0000-0000-000000000000")  # Placeholder
    
    result = await db.execute(
        select(DataImport)
        .where(DataImport.user_id == user_id)
        .order_by(DataImport.started_at.desc())
    )
    imports = result.scalars().all()
    
    return imports


@router.get("/imports/{import_id}", response_model=DataImportResponse)
async def get_import_status(
    import_id: UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
):
    """Get status of a data import"""
    import_record = await db.get(DataImport, import_id)
    
    if not import_record:
        raise HTTPException(status_code=404, detail="Import not found")
    
    # TODO: Verify user owns this import
    
    return import_record


@router.get("/metrics", response_model=List[DailyMetricResponse])
async def get_metrics(
    metric_type: str,
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
):
    """Get daily aggregated metrics for a date range"""
    # TODO: Get user_id from authenticated user
    user_id = UUID("00000000-0000-0000-0000-000000000000")  # Placeholder
    
    from app.services.health_data_service import get_daily_metrics
    
    metrics = await get_daily_metrics(
        str(user_id),
        metric_type,
        start_date,
        end_date,
        db,
    )
    
    return metrics
