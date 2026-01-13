"""
Analysis service for statistical analysis.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from uuid import UUID
from datetime import date, timedelta
import numpy as np
from scipy import stats
from app.models.intervention import Intervention
from app.models.health_metric import HealthMetric
from app.models.analysis_result import AnalysisResult
from app.schemas.analysis import InterventionAnalysisResponse, AnalysisResultResponse
from app.services.insight_generator import InsightGenerator


class AnalysisService:
    """Service for intervention analysis."""
    
    # Metrics to analyze
    DEFAULT_METRICS = ['hrv', 'resting_hr', 'sleep_duration', 'steps']
    
    def __init__(self, db: Session):
        self.db = db
        self.insight_generator = InsightGenerator()
    
    async def analyze_intervention(
        self, intervention_id: UUID, user_id: UUID
    ) -> Optional[InterventionAnalysisResponse]:
        """Run statistical analysis for an intervention."""
        intervention = self.db.query(Intervention).filter(
            Intervention.id == intervention_id,
            Intervention.user_id == user_id
        ).first()
        
        if not intervention:
            return None
        
        # Calculate date ranges
        baseline_start = intervention.start_date - timedelta(days=intervention.baseline_days)
        baseline_end = intervention.start_date
        intervention_start = intervention.start_date
        intervention_end = intervention.end_date or date.today()
        
        # Analyze each metric
        results = []
        
        for metric_type in self.DEFAULT_METRICS:
            # Get baseline data
            baseline_data = self._get_daily_averages(
                user_id, metric_type, baseline_start, baseline_end
            )
            
            # Get intervention data
            intervention_data = self._get_daily_averages(
                user_id, metric_type, intervention_start, intervention_end
            )
            
            # Need at least 7 days of data for meaningful analysis
            if len(baseline_data) < 7 or len(intervention_data) < 7:
                continue
            
            # Calculate statistics
            baseline_avg = np.mean(baseline_data)
            baseline_stddev = np.std(baseline_data, ddof=1) if len(baseline_data) > 1 else 0
            intervention_avg = np.mean(intervention_data)
            intervention_stddev = np.std(intervention_data, ddof=1) if len(intervention_data) > 1 else 0
            
            percent_change = ((intervention_avg - baseline_avg) / baseline_avg * 100) if baseline_avg != 0 else 0
            
            # T-test for significance
            t_stat, p_value = stats.ttest_ind(baseline_data, intervention_data)
            is_significant = p_value < 0.05
            
            # Generate insight
            insight = self.insight_generator.generate(
                metric_type,
                baseline_avg,
                intervention_avg,
                percent_change,
                is_significant,
                len(baseline_data),
                len(intervention_data)
            )
            
            # Save or update result
            result = self.db.query(AnalysisResult).filter(
                AnalysisResult.intervention_id == intervention_id,
                AnalysisResult.metric_type == metric_type
            ).first()
            
            if result:
                result.baseline_avg = baseline_avg
                result.baseline_stddev = baseline_stddev
                result.intervention_avg = intervention_avg
                result.intervention_stddev = intervention_stddev
                result.percent_change = percent_change
                result.p_value = float(p_value)
                result.is_significant = is_significant
                result.sample_size_baseline = len(baseline_data)
                result.sample_size_intervention = len(intervention_data)
                result.generated_insight = insight
            else:
                result = AnalysisResult(
                    intervention_id=intervention_id,
                    metric_type=metric_type,
                    baseline_avg=baseline_avg,
                    baseline_stddev=baseline_stddev,
                    intervention_avg=intervention_avg,
                    intervention_stddev=intervention_stddev,
                    percent_change=percent_change,
                    p_value=float(p_value),
                    is_significant=is_significant,
                    sample_size_baseline=len(baseline_data),
                    sample_size_intervention=len(intervention_data),
                    generated_insight=insight
                )
                self.db.add(result)
            
            results.append(AnalysisResultResponse.model_validate(result))
        
        self.db.commit()
        
        return InterventionAnalysisResponse(
            intervention_id=intervention.id,
            intervention_name=intervention.name,
            start_date=intervention.start_date.isoformat(),
            end_date=intervention.end_date.isoformat() if intervention.end_date else None,
            results=results
        )
    
    def _get_daily_averages(
        self, user_id: UUID, metric_type: str, start_date: date, end_date: date
    ) -> List[float]:
        """Get daily average values for a metric in a date range."""
        # Query daily aggregates
        query = self.db.query(
            func.date(HealthMetric.timestamp).label('day'),
            func.avg(HealthMetric.value).label('avg_value')
        ).filter(
            and_(
                HealthMetric.user_id == user_id,
                HealthMetric.metric_type == metric_type,
                func.date(HealthMetric.timestamp) >= start_date,
                func.date(HealthMetric.timestamp) <= end_date
            )
        ).group_by(func.date(HealthMetric.timestamp)).order_by('day')
        
        results = query.all()
        return [float(row.avg_value) for row in results if row.avg_value is not None]
    
    async def get_intervention_results(
        self, intervention_id: UUID, user_id: UUID
    ) -> Optional[InterventionAnalysisResponse]:
        """Get existing analysis results for an intervention."""
        intervention = self.db.query(Intervention).filter(
            Intervention.id == intervention_id,
            Intervention.user_id == user_id
        ).first()
        
        if not intervention:
            return None
        
        results = self.db.query(AnalysisResult).filter(
            AnalysisResult.intervention_id == intervention_id
        ).all()
        
        if not results:
            return None
        
        return InterventionAnalysisResponse(
            intervention_id=intervention.id,
            intervention_name=intervention.name,
            start_date=intervention.start_date.isoformat(),
            end_date=intervention.end_date.isoformat() if intervention.end_date else None,
            results=[AnalysisResultResponse.model_validate(r) for r in results]
        )
