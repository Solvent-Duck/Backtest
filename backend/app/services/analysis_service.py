"""
Service for statistical analysis of interventions
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, timedelta
from typing import List, Optional
import numpy as np
from scipy import stats

from app.models.intervention import Intervention
from app.models.analysis_result import AnalysisResult
from app.services.health_data_service import get_daily_metrics


async def analyze_intervention(
    intervention_id: str,
    db: AsyncSession,
) -> List[AnalysisResult]:
    """
    Analyze an intervention by comparing baseline vs intervention periods
    
    Returns list of analysis results for each metric
    """
    # Get intervention
    intervention = await db.get(Intervention, intervention_id)
    if not intervention:
        raise ValueError("Intervention not found")
    
    # Calculate date ranges
    baseline_start = intervention.start_date - timedelta(days=intervention.baseline_days)
    baseline_end = intervention.start_date
    
    intervention_start = intervention.start_date
    intervention_end = intervention.end_date or date.today()
    
    # Metrics to analyze
    metric_types = ["hrv", "resting_hr", "sleep_duration", "steps", "active_energy"]
    
    results = []
    
    for metric_type in metric_types:
        # Get baseline data
        baseline_data = await get_daily_metrics(
            str(intervention.user_id),
            metric_type,
            baseline_start,
            baseline_end,
            db,
        )
        
        # Get intervention data
        intervention_data = await get_daily_metrics(
            str(intervention.user_id),
            metric_type,
            intervention_start,
            intervention_end,
            db,
        )
        
        # Check if we have enough data
        if len(baseline_data) < 7 or len(intervention_data) < 7:
            continue  # Not enough data for meaningful analysis
        
        # Extract values
        baseline_values = [d["avg_value"] for d in baseline_data if d["avg_value"] is not None]
        intervention_values = [d["avg_value"] for d in intervention_data if d["avg_value"] is not None]
        
        if len(baseline_values) < 7 or len(intervention_values) < 7:
            continue
        
        # Calculate statistics
        baseline_avg = np.mean(baseline_values)
        baseline_stddev = np.std(baseline_values, ddof=1) if len(baseline_values) > 1 else 0.0
        
        intervention_avg = np.mean(intervention_values)
        intervention_stddev = np.std(intervention_values, ddof=1) if len(intervention_values) > 1 else 0.0
        
        # Calculate percent change
        if baseline_avg != 0:
            percent_change = ((intervention_avg - baseline_avg) / baseline_avg) * 100
        else:
            percent_change = 0.0
        
        # T-test for significance
        t_stat, p_value = stats.ttest_ind(baseline_values, intervention_values)
        is_significant = p_value < 0.05
        
        # Generate insight
        insight = generate_insight(
            metric_type,
            baseline_avg,
            intervention_avg,
            percent_change,
            is_significant,
            len(baseline_values),
            len(intervention_values),
        )
        
        # Create or update analysis result
        existing_result = await db.execute(
            select(AnalysisResult).where(
                AnalysisResult.intervention_id == intervention_id,
                AnalysisResult.metric_type == metric_type,
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            # Update existing
            existing.baseline_avg = baseline_avg
            existing.baseline_stddev = baseline_stddev
            existing.intervention_avg = intervention_avg
            existing.intervention_stddev = intervention_stddev
            existing.percent_change = percent_change
            existing.p_value = float(p_value)
            existing.is_significant = is_significant
            existing.sample_size_baseline = len(baseline_values)
            existing.sample_size_intervention = len(intervention_values)
            existing.generated_insight = insight
            result = existing
        else:
            # Create new
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
                sample_size_baseline=len(baseline_values),
                sample_size_intervention=len(intervention_values),
                generated_insight=insight,
            )
            db.add(result)
        
        results.append(result)
    
    await db.commit()
    
    return results


def generate_insight(
    metric_type: str,
    baseline: float,
    intervention: float,
    change: float,
    significant: bool,
    n_baseline: int,
    n_intervention: int,
) -> str:
    """Generate plain-language insight from statistical results"""
    
    metric_names = {
        "hrv": "HRV",
        "resting_hr": "resting heart rate",
        "sleep_duration": "sleep duration",
        "steps": "daily steps",
        "active_energy": "active energy burned",
    }
    
    metric_units = {
        "hrv": "ms",
        "resting_hr": "bpm",
        "sleep_duration": "hours",
        "steps": "steps",
        "active_energy": "kcal",
    }
    
    direction = "increased" if change > 0 else "decreased"
    abs_change = abs(change)
    
    metric_name = metric_names.get(metric_type, metric_type)
    unit = metric_units.get(metric_type, "")
    
    insight = f"Your {metric_name} {direction} by {abs_change:.1f}%"
    
    if significant:
        insight += " (statistically significant, p<0.05)"
    else:
        insight += " (not statistically significant)"
    
    insight += f". Baseline average: {baseline:.2f} {unit}, Intervention average: {intervention:.2f} {unit}."
    insight += f" Sample size: {n_baseline} baseline days, {n_intervention} intervention days."
    
    # Add interpretation
    if metric_type == "hrv" and change > 10 and significant:
        insight += " This is a meaningful improvement in heart rate variability, suggesting better recovery and reduced stress."
    elif metric_type == "resting_hr" and change < -5 and significant:
        insight += " This reduction in resting heart rate suggests improved cardiovascular fitness."
    elif metric_type == "sleep_duration" and change > 10 and significant:
        insight += " This increase in sleep duration may contribute to better recovery and overall health."
    
    return insight
