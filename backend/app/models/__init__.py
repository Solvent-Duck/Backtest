"""
Import all models for Alembic to detect them.
"""
from app.models.user import User
from app.models.intervention import Intervention
from app.models.health_metric import HealthMetric
from app.models.analysis_result import AnalysisResult
from app.models.data_import import DataImport

__all__ = [
    "User",
    "Intervention",
    "HealthMetric",
    "AnalysisResult",
    "DataImport",
]
