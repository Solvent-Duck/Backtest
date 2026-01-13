"""
Celery tasks for processing health data
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from celery_app import celery_app
from app.services.health_data_service import process_health_export
from app.core.database import AsyncSessionLocal
import asyncio


@celery_app.task(bind=True, name="process_health_export")
def process_health_export_task(self, file_path: str, user_id: str, import_id: str):
    """
    Celery task to process health export file
    
    Note: This is a synchronous wrapper around async code
    """
    async def run():
        async with AsyncSessionLocal() as db:
            try:
                records = await process_health_export(file_path, user_id, import_id, db)
                return {"status": "completed", "records_imported": records}
            except Exception as e:
                return {"status": "failed", "error": str(e)}
    
    # Run async function in sync context
    result = asyncio.run(run())
    
    if result["status"] == "failed":
        raise Exception(result.get("error", "Unknown error"))
    
    return result
