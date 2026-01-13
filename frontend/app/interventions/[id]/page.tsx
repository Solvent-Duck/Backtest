'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { api } from '@/lib/api'
import Link from 'next/link'
import { format } from 'date-fns'

export default function InterventionDetailPage() {
  const params = useParams()
  const id = params.id as string

  const { data: intervention, isLoading } = useQuery({
    queryKey: ['intervention', id],
    queryFn: () => api.getIntervention(id),
  })

  const { data: results } = useQuery({
    queryKey: ['intervention-results', id],
    queryFn: () => api.getInterventionResults(id),
    enabled: !!intervention,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">Loading...</div>
      </div>
    )
  }

  if (!intervention) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <p>Intervention not found</p>
          <Link href="/dashboard" className="text-blue-600 hover:underline">
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <Link
          href="/dashboard"
          className="text-blue-600 hover:underline mb-4 inline-block"
        >
          ← Back to Dashboard
        </Link>

        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">{intervention.name}</h1>
          <div className="flex gap-4 text-gray-600">
            <span>Category: {intervention.category}</span>
            <span>•</span>
            <span>
              Started: {format(new Date(intervention.start_date), 'MMM d, yyyy')}
            </span>
            <span>•</span>
            <span
              className={`px-2 py-1 rounded ${
                intervention.status === 'active'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {intervention.status}
            </span>
          </div>
        </div>

        {results && results.results.length > 0 ? (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold">Analysis Results</h2>
            {results.results.map((result) => (
              <div
                key={result.id}
                className="p-6 border rounded-lg bg-white shadow-sm"
              >
                <h3 className="text-xl font-semibold mb-2 uppercase">
                  {result.metric_type}
                </h3>
                {result.generated_insight && (
                  <p className="text-gray-700 mb-4">{result.generated_insight}</p>
                )}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500">Baseline Avg</div>
                    <div className="font-semibold">
                      {result.baseline_avg?.toFixed(2)}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-500">Intervention Avg</div>
                    <div className="font-semibold">
                      {result.intervention_avg?.toFixed(2)}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-500">Change</div>
                    <div
                      className={`font-semibold ${
                        (result.percent_change || 0) > 0
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      {result.percent_change?.toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-500">Significant</div>
                    <div
                      className={`font-semibold ${
                        result.is_significant ? 'text-green-600' : 'text-gray-600'
                      }`}
                    >
                      {result.is_significant ? 'Yes' : 'No'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">
              No analysis results yet. Upload health data and run analysis.
            </p>
            <button
              onClick={() => {
                api.analyzeIntervention(id).then(() => {
                  window.location.reload()
                })
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Run Analysis
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
