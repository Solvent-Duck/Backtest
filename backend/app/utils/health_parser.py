"""
Apple Health XML parser using lxml
"""
import lxml.etree as ET
from typing import Iterator, Dict, Optional
from datetime import datetime
import zipfile
import io


class HealthRecord:
    """Represents a single health record from Apple Health export"""
    
    def __init__(
        self,
        record_type: str,
        value: Optional[str],
        unit: Optional[str],
        start_date: datetime,
        end_date: Optional[datetime],
        source: Optional[str],
    ):
        self.record_type = record_type
        self.value = value
        self.unit = unit
        self.start_date = start_date
        self.end_date = end_date
        self.source = source
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "record_type": self.record_type,
            "value": self.value,
            "unit": self.unit,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "source": self.source,
        }


def parse_iso_datetime(date_str: str) -> datetime:
    """Parse ISO datetime string from Apple Health export"""
    # Apple Health format: "2025-01-01 23:30:00 -0800"
    # Remove timezone offset for parsing (we'll handle timezone separately)
    try:
        # Try parsing with timezone
        if " " in date_str and len(date_str.split()) >= 3:
            date_part = " ".join(date_str.split()[:-1])
            return datetime.strptime(date_part, "%Y-%m-%d %H:%M:%S")
        else:
            return datetime.fromisoformat(date_str.replace(" ", "T"))
    except Exception:
        # Fallback
        return datetime.strptime(date_str.split(" ")[0], "%Y-%m-%d")


def parse_apple_health_xml(file_path: str) -> Iterator[HealthRecord]:
    """
    Stream parse large Apple Health XML files efficiently
    
    Uses iterparse to avoid loading entire file into memory
    """
    context = ET.iterparse(file_path, events=("end",), tag="Record", huge_tree=True)
    
    for event, elem in context:
        try:
            record_type = elem.get("type", "")
            value = elem.get("value")
            unit = elem.get("unit")
            start_date_str = elem.get("startDate")
            end_date_str = elem.get("endDate")
            source = elem.get("sourceName")
            
            if not start_date_str:
                continue
            
            start_date = parse_iso_datetime(start_date_str)
            end_date = parse_iso_datetime(end_date_str) if end_date_str else start_date
            
            record = HealthRecord(
                record_type=record_type,
                value=value,
                unit=unit,
                start_date=start_date,
                end_date=end_date,
                source=source,
            )
            
            yield record
            
        except Exception as e:
            # Log error but continue parsing
            print(f"Error parsing record: {e}")
            continue
        finally:
            # Clear element to save memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]


def extract_zip_file(zip_path: str) -> Optional[str]:
    """
    Extract Apple Health export ZIP file and return path to export.xml
    
    Apple Health exports are ZIP files containing export.xml
    """
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # Find export.xml in the zip
            xml_files = [f for f in zip_ref.namelist() if f.endswith(".xml") and "export" in f.lower()]
            
            if not xml_files:
                raise ValueError("No export.xml found in ZIP file")
            
            # Extract to temporary location
            xml_file = xml_files[0]
            zip_ref.extract(xml_file, "/tmp")
            
            return f"/tmp/{xml_file}"
    except Exception as e:
        print(f"Error extracting ZIP: {e}")
        return None


# Metric type mapping from Apple Health to our internal types
METRIC_TYPE_MAPPING = {
    "HKCategoryTypeIdentifierSleepAnalysis": "sleep_duration",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "hrv",
    "HKQuantityTypeIdentifierRestingHeartRate": "resting_hr",
    "HKQuantityTypeIdentifierStepCount": "steps",
    "HKQuantityTypeIdentifierActiveEnergyBurned": "active_energy",
    "HKQuantityTypeIdentifierAppleExerciseTime": "exercise_minutes",
    "HKQuantityTypeIdentifierBodyTemperature": "body_temp",
    "HKQuantityTypeIdentifierOxygenSaturation": "blood_oxygen",
}


def map_metric_type(apple_health_type: str) -> Optional[str]:
    """Map Apple Health metric type to our internal metric type"""
    return METRIC_TYPE_MAPPING.get(apple_health_type)


def calculate_sleep_duration(start: datetime, end: datetime) -> float:
    """Calculate sleep duration in hours"""
    if not end:
        return 0.0
    duration = end - start
    return duration.total_seconds() / 3600.0
