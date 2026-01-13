"""
Health data service for business logic.
"""
import os
import zipfile
import aiofiles
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime
from fastapi import UploadFile
from app.core.config import settings
from app.models.data_import import DataImport
from app.models.health_metric import HealthMetric
from app.schemas.data_import import DataImportResponse
from app.services.health_parser import AppleHealthParser


class HealthDataService:
    """Service for health data operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.parser = AppleHealthParser()
    
    async def create_import_record(
        self, user_id: UUID, filename: str, file_size: int
    ) -> DataImportResponse:
        """Create a data import record."""
        import_record = DataImport(
            user_id=user_id,
            filename=filename,
            file_size_mb=file_size / (1024 * 1024),
            status="pending"
        )
        self.db.add(import_record)
        self.db.commit()
        self.db.refresh(import_record)
        return DataImportResponse.model_validate(import_record)
    
    async def store_temp_file(
        self, file: UploadFile, import_id: UUID
    ) -> str:
        """Store uploaded file temporarily."""
        os.makedirs(settings.TEMP_STORAGE_PATH, exist_ok=True)
        file_path = os.path.join(settings.TEMP_STORAGE_PATH, f"{import_id}.zip")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path
    
    async def list_imports(self, user_id: UUID) -> List[DataImportResponse]:
        """List all imports for a user."""
        imports = self.db.query(DataImport).filter(
            DataImport.user_id == user_id
        ).order_by(DataImport.started_at.desc()).all()
        
        return [DataImportResponse.model_validate(i) for i in imports]
    
    async def get_import(
        self, import_id: UUID, user_id: UUID
    ) -> Optional[DataImportResponse]:
        """Get a specific import."""
        import_record = self.db.query(DataImport).filter(
            DataImport.id == import_id,
            DataImport.user_id == user_id
        ).first()
        
        if not import_record:
            return None
        
        return DataImportResponse.model_validate(import_record)
    
    def process_import(
        self, import_id: UUID, file_path: str, user_id: UUID
    ) -> None:
        """Process a health data import."""
        import_record = self.db.query(DataImport).filter(
            DataImport.id == import_id
        ).first()
        
        if not import_record:
            return
        
        try:
            import_record.status = "processing"
            self.db.commit()
            
            # Extract ZIP if needed
            xml_path = file_path
            if file_path.endswith('.zip'):
                extract_path = file_path.replace('.zip', '_extracted')
                os.makedirs(extract_path, exist_ok=True)
                
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                
                # Find XML file
                for root, dirs, files in os.walk(extract_path):
                    for file in files:
                        if file.endswith('.xml'):
                            xml_path = os.path.join(root, file)
                            break
            
            # Parse XML
            records = self.parser.parse_file(xml_path)
            
            # Insert records in batches
            batch_size = 1000
            records_imported = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                metrics = [
                    HealthMetric(
                        user_id=user_id,
                        metric_type=record['metric_type'],
                        value=record['value'],
                        unit=record.get('unit'),
                        date=record['date'],
                        timestamp=record['timestamp'],
                        source_device=record.get('source_device'),
                        metadata=record.get('metadata')
                    )
                    for record in batch
                ]
                self.db.bulk_save_objects(metrics)
                self.db.commit()
                records_imported += len(batch)
            
            import_record.status = "completed"
            import_record.records_imported = records_imported
            import_record.completed_at = datetime.utcnow()
            self.db.commit()
            
            # Cleanup temp files
            if os.path.exists(file_path):
                os.remove(file_path)
            if file_path.endswith('.zip') and os.path.exists(extract_path):
                import shutil
                shutil.rmtree(extract_path)
            
        except Exception as e:
            import_record.status = "failed"
            import_record.error_message = str(e)
            import_record.completed_at = datetime.utcnow()
            self.db.commit()
            raise
    
    async def get_metrics(
        self, user_id: UUID, metric_type: Optional[str] = None,
        start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[Dict]:
        """Get health metrics for a user."""
        query = self.db.query(HealthMetric).filter(HealthMetric.user_id == user_id)
        
        if metric_type:
            query = query.filter(HealthMetric.metric_type == metric_type)
        
        if start_date:
            query = query.filter(HealthMetric.date >= datetime.fromisoformat(start_date).date())
        
        if end_date:
            query = query.filter(HealthMetric.date <= datetime.fromisoformat(end_date).date())
        
        metrics = query.order_by(HealthMetric.timestamp).all()
        
        return [
            {
                "id": str(m.id),
                "metric_type": m.metric_type,
                "value": m.value,
                "unit": m.unit,
                "date": m.date.isoformat(),
                "timestamp": m.timestamp.isoformat(),
                "source_device": m.source_device,
            }
            for m in metrics
        ]
