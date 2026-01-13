"""
Apple Health XML parser.
"""
import lxml.etree as ET
from datetime import datetime
from typing import List, Dict, Iterator
from dateutil import parser as date_parser


class AppleHealthParser:
    """Parser for Apple Health XML exports."""
    
    # Mapping from Apple Health types to our metric types
    METRIC_MAPPING = {
        'HKCategoryTypeIdentifierSleepAnalysis': 'sleep_duration',
        'HKQuantityTypeIdentifierHeartRateVariabilitySDNN': 'hrv',
        'HKQuantityTypeIdentifierRestingHeartRate': 'resting_hr',
        'HKQuantityTypeIdentifierStepCount': 'steps',
        'HKQuantityTypeIdentifierActiveEnergyBurned': 'active_energy',
        'HKQuantityTypeIdentifierAppleExerciseTime': 'exercise_minutes',
        'HKQuantityTypeIdentifierBodyTemperature': 'body_temp',
        'HKQuantityTypeIdentifierOxygenSaturation': 'blood_oxygen',
    }
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """Parse Apple Health XML file and return list of health records."""
        records = []
        
        # Use iterparse for memory efficiency with large files
        context = ET.iterparse(file_path, events=('end',), tag='Record')
        
        for event, elem in context:
            try:
                record = self._parse_record(elem)
                if record:
                    records.append(record)
            except Exception as e:
                # Log error but continue parsing
                print(f"Error parsing record: {e}")
                continue
            finally:
                # Clear element to save memory
                elem.clear()
                while elem.getparent() is not None:
                    del elem.getparent()[0]
        
        return records
    
    def _parse_record(self, elem: ET.Element) -> Dict:
        """Parse a single Record element."""
        record_type = elem.get('type')
        
        # Map to our metric type
        metric_type = self.METRIC_MAPPING.get(record_type)
        if not metric_type:
            return None  # Skip unmapped types
        
        # Parse dates
        start_date_str = elem.get('startDate')
        end_date_str = elem.get('endDate')
        
        if not start_date_str:
            return None
        
        try:
            start_date = date_parser.parse(start_date_str)
            end_date = date_parser.parse(end_date_str) if end_date_str else start_date
        except Exception:
            return None
        
        # Parse value
        value_str = elem.get('value')
        if not value_str:
            return None
        
        # Handle different value types
        if record_type == 'HKCategoryTypeIdentifierSleepAnalysis':
            # For sleep, calculate duration in hours
            duration = (end_date - start_date).total_seconds() / 3600
            value = duration
        else:
            try:
                value = float(value_str)
            except ValueError:
                return None
        
        return {
            'metric_type': metric_type,
            'value': value,
            'unit': elem.get('unit'),
            'date': start_date.date(),
            'timestamp': start_date,
            'source_device': elem.get('sourceName'),
            'metadata': {
                'original_type': record_type,
                'source_version': elem.get('sourceVersion'),
            }
        }
    
    def parse_stream(self, file_path: str) -> Iterator[Dict]:
        """Stream parse large XML files (generator)."""
        context = ET.iterparse(file_path, events=('end',), tag='Record')
        
        for event, elem in context:
            try:
                record = self._parse_record(elem)
                if record:
                    yield record
            except Exception:
                continue
            finally:
                elem.clear()
                while elem.getparent() is not None:
                    del elem.getparent()[0]
