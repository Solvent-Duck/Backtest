"""
Insight generator for plain-language interpretation of results.
"""
from typing import Dict


class InsightGenerator:
    """Generates plain-language insights from statistical results."""
    
    METRIC_NAMES: Dict[str, str] = {
        'hrv': 'HRV',
        'resting_hr': 'resting heart rate',
        'sleep_duration': 'sleep duration',
        'steps': 'daily steps',
        'active_energy': 'active energy burned',
        'exercise_minutes': 'exercise minutes',
    }
    
    METRIC_UNITS: Dict[str, str] = {
        'hrv': 'ms',
        'resting_hr': 'bpm',
        'sleep_duration': 'hours',
        'steps': 'steps',
        'active_energy': 'kcal',
        'exercise_minutes': 'minutes',
    }
    
    def generate(
        self,
        metric_type: str,
        baseline_avg: float,
        intervention_avg: float,
        percent_change: float,
        is_significant: bool,
        n_baseline: int,
        n_intervention: int
    ) -> str:
        """Generate insight text."""
        metric_name = self.METRIC_NAMES.get(metric_type, metric_type)
        unit = self.METRIC_UNITS.get(metric_type, '')
        
        direction = "increased" if percent_change > 0 else "decreased"
        abs_change = abs(percent_change)
        
        # Base insight
        insight = f"Your {metric_name} {direction} by {abs_change:.1f}%"
        
        if is_significant:
            insight += " (statistically significant, p<0.05)"
        else:
            insight += " (not statistically significant)"
        
        insight += f". Baseline average: {baseline_avg:.1f} {unit}, intervention average: {intervention_avg:.1f} {unit}."
        insight += f" Sample size: {n_baseline} baseline days, {n_intervention} intervention days."
        
        # Add interpretation based on metric type and change
        interpretation = self._get_interpretation(metric_type, percent_change, is_significant)
        if interpretation:
            insight += f" {interpretation}"
        
        return insight
    
    def _get_interpretation(
        self, metric_type: str, percent_change: float, is_significant: bool
    ) -> str:
        """Get interpretation based on metric type."""
        if not is_significant:
            return "This change may be due to natural variation rather than the intervention."
        
        interpretations = {
            'hrv': {
                'positive': "This is a meaningful improvement in heart rate variability, suggesting better recovery and reduced stress.",
                'negative': "This decrease in HRV may indicate increased stress or reduced recovery capacity."
            },
            'resting_hr': {
                'positive': "This reduction in resting heart rate suggests improved cardiovascular fitness.",
                'negative': "This increase in resting heart rate may indicate increased stress or reduced fitness."
            },
            'sleep_duration': {
                'positive': "This increase in sleep duration is beneficial for recovery and overall health.",
                'negative': "This decrease in sleep duration may negatively impact recovery and health."
            },
            'steps': {
                'positive': "This increase in daily activity is beneficial for cardiovascular health and fitness.",
                'negative': "This decrease in activity may negatively impact fitness and health."
            }
        }
        
        metric_interpretations = interpretations.get(metric_type)
        if not metric_interpretations:
            return ""
        
        change_type = 'positive' if percent_change > 0 else 'negative'
        return metric_interpretations.get(change_type, "")
