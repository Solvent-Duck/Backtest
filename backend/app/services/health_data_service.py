"""
Service for processing and storing health data
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date
from typing import List, Optional
import os

from app.models.health_metric import HealthMetric
from app.models.data_import import DataImport
from app.utils.health_parser import (
    parse_apple_health_xml,
    extract_zip_file,
    map_metric_type,
    calculate_sleep_duration,
)


async def process_health_export(
    file_path: str,
    user_id: str,
    import_id: str,
    db: AsyncSession,
) -> int:
    """
    Process Apple Health export file and store metrics in database
    
    Returns number of records imported
    """
    # Extract ZIP if needed
    if file_path.endswith(".zip"):
        xml_path = extract_zip_file(file_path)
        if not xml_path:
            raise ValueError("Failed to extract ZIP file")
    else:
        xml_path = file_path
    
    records_imported = 0
    batch = []
    batch_size = 1000
    
    try:
        # Update import status
        import_record = await db.get(DataImport, import_id)
        if import_record:
            import_record.status = "processing"
            await db.commit()
        
        # Parse XML and insert in batches
        for record in parse_apple_health_xml(xml_path):
            metric_type = map_metric_type(record.record_type)
            
            if not metric_type:
                continue  # Skip unmapped metrics
            
            # Handle sleep duration specially
            if metric_type == "sleep_duration":
                value = calculate_sleep_duration(record.start_date, record.end_date)
                unit = "hours"
            else:
                try:
                    value = float(record.value) if record.value else None
                except (ValueError, TypeError):
                    continue
                
                if value is None:
                    continue
                
                unit = record.unit
            
            # Create health metric
            health_metric = HealthMetric(
                user_id=user_id,
                metric_type=metric_type,
                value=value,
                unit=unit,
                date=record.start_date.date(),
                timestamp=record.start_date,
                source_device=record.source,
            )
            
            batch.append(health_metric)
            
            # Insert batch when full
            if len(batch) >= batch_size:
                db.add_all(batch)
                await db.commit()
                records_imported += len(batch)
                batch = []
        
        # Insert remaining records
        if batch:
            db.add_all(batch)
            await db.commit()
            records_imported += len(batch)
        
        # Update import record
        if import_record:
            import_record.status = "completed"
            import_record.records_imported = records_imported
            import_record.completed_at = datetime.utcnow()
            await db.commit()
        
        # Clean up extracted file
        if file_path.endswith(".zip") and xml_path and os.path.exists(xml_path):
            os.remove(xml_path)
        
        return records_imported
        
    except Exception as e:
        # Update import record with error
        import_record = await db.get(DataImport, import_id)
        if import_record:
            import_record.status = "failed"
            import_record.error_message = str(e)
            import_record.completed_at = datetime.utcnow()
            await db.commit()
        raise


async def get_daily_metrics(
    user_id: str,
    metric_type: str,
    start_date: date,
    end_date: date,
    db: AsyncSession,
) -> List[dict]:
    """
    Get daily aggregated metrics for a user and date range
    
    Uses TimescaleDB continuous aggregates if available, otherwise calculates on the fly
    """
    query = select(
        func.date(HealthMetric.date).label("day"),
        func.avg(HealthMetric.value).label("avg_value"),
        func.stddev(HealthMetric.value).label("stddev_value"),
        func.min(HealthMetric.value).label("min_value"),
        func.max(HealthMetric.value).label("max_value"),
        func.count(HealthMetric.id).label("sample_size"),
    ).where(
        HealthMetric.user_id == user_id,
        HealthMetric.metric_type == metric_type,
        HealthMetric.date >= start_date,
        HealthMetric.date <= end_date,
    ).group_by(
        func.date(HealthMetric.date)
    ).order_by(
        func.date(HealthMetric.date)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        {
            "day": row.day.isoformat(),
            "metric_type": metric_type,
            "avg_value": float(row.avg_value) if row.avg_value else None,
            "stddev_value": float(row.stddev_value) if row.stddev_value else None,
            "min_value": float(row.min_value) if row.min_value else None,
            "max_value": float(row.max_value) if row.max_value else None,
            "sample_size": row.sample_size,
        }
        for row in rows
    ]
