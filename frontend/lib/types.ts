/**
 * TypeScript types for API responses
 */

export interface Intervention {
  id: string;
  user_id: string;
  name: string;
  category: "supplement" | "diet" | "exercise" | "sleep" | "stress" | "other";
  dosage?: string;
  start_date: string;
  end_date?: string;
  baseline_days: number;
  status: "active" | "completed" | "abandoned";
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface InterventionCreate {
  name: string;
  category: "supplement" | "diet" | "exercise" | "sleep" | "stress" | "other";
  dosage?: string;
  start_date: string;
  end_date?: string;
  baseline_days?: number;
  notes?: string;
}

export interface DailyMetric {
  day: string;
  metric_type: string;
  avg_value: number;
  stddev_value?: number;
  min_value?: number;
  max_value?: number;
  sample_size: number;
}

export interface AnalysisResult {
  id: string;
  intervention_id: string;
  metric_type: string;
  baseline_avg?: number;
  baseline_stddev?: number;
  intervention_avg?: number;
  intervention_stddev?: number;
  percent_change?: number;
  p_value?: number;
  is_significant?: boolean;
  sample_size_baseline?: number;
  sample_size_intervention?: number;
  generated_insight?: string;
  created_at: string;
}

export interface InterventionAnalysis {
  intervention_id: string;
  results: AnalysisResult[];
  summary: {
    total_metrics_analyzed: number;
    significant_changes: number;
    intervention_name: string;
    intervention_start: string;
    intervention_end?: string;
  };
}

export interface DataImport {
  id: string;
  user_id: string;
  filename?: string;
  file_size_mb?: number;
  records_imported?: number;
  status: "pending" | "processing" | "completed" | "failed";
  error_message?: string;
  started_at: string;
  completed_at?: string;
}
