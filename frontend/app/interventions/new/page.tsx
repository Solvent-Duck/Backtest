'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from '@tanstack/react-query'
import { api, InterventionCreate } from '@/lib/api'

export default function NewInterventionPage() {
  const router = useRouter()
  const [formData, setFormData] = useState<InterventionCreate>({
    name: '',
    category: 'supplement',
    dosage: '',
    start_date: new Date().toISOString().split('T')[0],
    baseline_days: 14,
  })

  const mutation = useMutation({
    mutationFn: (data: InterventionCreate) => api.createIntervention(data),
    onSuccess: () => {
      router.push('/dashboard')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(formData)
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">New Intervention</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">
              Intervention Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Magnesium Glycinate"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Category *
            </label>
            <select
              required
              value={formData.category}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  category: e.target.value as InterventionCreate['category'],
                })
              }
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="supplement">Supplement</option>
              <option value="diet">Diet Change</option>
              <option value="exercise">Exercise Protocol</option>
              <option value="sleep">Sleep Intervention</option>
              <option value="stress">Stress Management</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Dosage/Details
            </label>
            <input
              type="text"
              value={formData.dosage || ''}
              onChange={(e) => setFormData({ ...formData, dosage: e.target.value })}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., 400mg daily"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Start Date *
            </label>
            <input
              type="date"
              required
              value={formData.start_date}
              onChange={(e) =>
                setFormData({ ...formData, start_date: e.target.value })
              }
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Baseline Days (before intervention)
            </label>
            <input
              type="number"
              min="7"
              max="30"
              value={formData.baseline_days || 14}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  baseline_days: parseInt(e.target.value) || 14,
                })
              }
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Notes</label>
            <textarea
              value={formData.notes || ''}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={4}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Any additional notes about this intervention..."
            />
          </div>

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={mutation.isPending}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {mutation.isPending ? 'Creating...' : 'Create Intervention'}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 border rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
