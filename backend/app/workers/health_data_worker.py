"""
Background worker for processing health data imports.
"""
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.health_data_service import HealthDataService
from uuid import UUID


@celery_app.task(bind=True, name="process_health_export")
def process_health_export(self, file_path: str, import_id: str, user_id: str):
    """Process Apple Health export file in background."""
    db = SessionLocal()
    try:
        service = HealthDataService(db)
        service.process_import(UUID(import_id), file_path, UUID(user_id))
        
        return {
            "status": "completed",
            "import_id": import_id
        }
    except Exception as e:
        # Update import record with error
        db.rollback()
        raise
    finally:
        db.close()
