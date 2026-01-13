'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { api } from '@/lib/api'
import { format } from 'date-fns'

export default function DashboardPage() {
  const { data: interventions, isLoading } = useQuery({
    queryKey: ['interventions'],
    queryFn: () => api.getInterventions(),
  })

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <Link
            href="/interventions/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            New Intervention
          </Link>
        </div>

        {isLoading ? (
          <div className="text-center py-12">Loading...</div>
        ) : interventions && interventions.length > 0 ? (
          <div className="grid gap-4">
            {interventions.map((intervention) => (
              <Link
                key={intervention.id}
                href={`/interventions/${intervention.id}`}
                className="block p-6 border rounded-lg hover:border-blue-500 transition"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-semibold mb-2">
                      {intervention.name}
                    </h2>
                    <p className="text-gray-600 mb-1">
                      Category: {intervention.category}
                    </p>
                    <p className="text-sm text-gray-500">
                      Started: {format(new Date(intervention.start_date), 'MMM d, yyyy')}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm ${
                      intervention.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : intervention.status === 'completed'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {intervention.status}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">No interventions yet.</p>
            <Link
              href="/interventions/new"
              className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Create Your First Intervention
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
