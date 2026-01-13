import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Intervention {
  id: string
  user_id: string
  name: string
  category: string
  dosage?: string
  start_date: string
  end_date?: string
  baseline_days: number
  status: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface InterventionCreate {
  name: string
  category: 'supplement' | 'diet' | 'exercise' | 'sleep' | 'stress' | 'other'
  dosage?: string
  start_date: string
  end_date?: string
  baseline_days?: number
  notes?: string
}

export interface DataImport {
  id: string
  user_id: string
  filename?: string
  file_size_mb?: number
  records_imported?: number
  status: string
  error_message?: string
  started_at: string
  completed_at?: string
}

export interface AnalysisResult {
  id: string
  intervention_id: string
  metric_type: string
  baseline_avg?: number
  baseline_stddev?: number
  intervention_avg?: number
  intervention_stddev?: number
  percent_change?: number
  p_value?: number
  is_significant?: boolean
  sample_size_baseline?: number
  sample_size_intervention?: number
  generated_insight?: string
  created_at: string
}

export interface InterventionAnalysis {
  intervention_id: string
  intervention_name: string
  start_date: string
  end_date?: string
  results: AnalysisResult[]
}

export const api = {
  // Interventions
  getInterventions: async (): Promise<Intervention[]> => {
    const response = await apiClient.get('/interventions')
    return response.data
  },

  getIntervention: async (id: string): Promise<Intervention> => {
    const response = await apiClient.get(`/interventions/${id}`)
    return response.data
  },

  createIntervention: async (data: InterventionCreate): Promise<Intervention> => {
    const response = await apiClient.post('/interventions', data)
    return response.data
  },

  updateIntervention: async (
    id: string,
    data: Partial<InterventionCreate>
  ): Promise<Intervention> => {
    const response = await apiClient.patch(`/interventions/${id}`, data)
    return response.data
  },

  deleteIntervention: async (id: string): Promise<void> => {
    await apiClient.delete(`/interventions/${id}`)
  },

  // Health Data
  uploadHealthData: async (file: File): Promise<DataImport> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post('/health-data/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getImports: async (): Promise<DataImport[]> => {
    const response = await apiClient.get('/health-data/imports')
    return response.data
  },

  getImportStatus: async (id: string): Promise<DataImport> => {
    const response = await apiClient.get(`/health-data/imports/${id}`)
    return response.data
  },

  getMetrics: async (params?: {
    metric_type?: string
    start_date?: string
    end_date?: string
  }): Promise<any[]> => {
    const response = await apiClient.get('/health-data/metrics', { params })
    return response.data
  },

  // Analysis
  analyzeIntervention: async (id: string): Promise<InterventionAnalysis> => {
    const response = await apiClient.post(`/analysis/interventions/${id}/analyze`)
    return response.data
  },

  getInterventionResults: async (id: string): Promise<InterventionAnalysis> => {
    const response = await apiClient.get(`/analysis/interventions/${id}/results`)
    return response.data
  },
}
