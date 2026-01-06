'use client'

import { useState, useEffect } from 'react'
import { Bell, Plus, Edit2, Trash2, CheckCircle, X } from 'lucide-react'
import api from '@/lib/api'
import { toast } from 'sonner'

interface Alert {
  id: string
  name: string
  keywords: string[]
  location_filter: string | null
  category_filter: string | null
  min_budget: number | null
  max_budget: number | null
  is_active: boolean
  created_at: string
}

interface AlertFormData {
  name: string
  keywords: string
  location_filter: string
  category_filter: string
  min_budget: string
  max_budget: string
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [formData, setFormData] = useState<AlertFormData>({
    name: '',
    keywords: '',
    location_filter: '',
    category_filter: '',
    min_budget: '',
    max_budget: '',
  })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get('/alerts')
      setAlerts(response.data.items || [])
    } catch (err: any) {
      console.error('Error fetching alerts:', err)
      setError(err.response?.data?.detail || 'Failed to fetch alerts')
    } finally {
      setLoading(false)
    }
  }

  const toggleAlert = async (alertId: string, currentStatus: boolean) => {
    try {
      const newStatus = !currentStatus
      await api.patch(`/alerts/${alertId}/toggle?is_active=${newStatus}`)
      setAlerts(alerts.map(alert =>
        alert.id === alertId ? { ...alert, is_active: newStatus } : alert
      ))
    } catch (err: any) {
      console.error('Error toggling alert:', err)
      alert('Failed to toggle alert status')
    }
  }

  const deleteAlert = async (alertId: string) => {
    if (!confirm('Are you sure you want to delete this alert?')) return

    try {
      await api.delete(`/alerts/${alertId}`)
      setAlerts(alerts.filter(alert => alert.id !== alertId))
      toast.success('Alert deleted successfully')
    } catch (err: any) {
      console.error('Error deleting alert:', err)
      toast.error(err.response?.data?.detail || 'Failed to delete alert')
    }
  }

  const createAlert = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.name.trim()) {
      toast.error('Alert name is required')
      return
    }

    try {
      setSubmitting(true)
      const payload = {
        name: formData.name,
        keywords: formData.keywords.split(',').map(k => k.trim()).filter(k => k),
        location_filter: formData.location_filter || null,
        category_filter: formData.category_filter || null,
        min_budget: formData.min_budget ? parseFloat(formData.min_budget) : null,
        max_budget: formData.max_budget ? parseFloat(formData.max_budget) : null,
        is_active: true,
      }

      const response = await api.post('/alerts', payload)
      setAlerts([response.data, ...alerts])
      setShowCreateModal(false)
      setFormData({
        name: '',
        keywords: '',
        location_filter: '',
        category_filter: '',
        min_budget: '',
        max_budget: '',
      })
      toast.success('Alert created successfully')
    } catch (err: any) {
      console.error('Error creating alert:', err)
      toast.error(err.response?.data?.detail || 'Failed to create alert')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Alert Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Create and manage tender alerts based on your preferences
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <Plus size={20} />
          Create Alert
        </button>
      </div>

      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading alerts...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          {alerts.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
              <Bell size={64} className="mx-auto text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                No alerts configured
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Create your first alert to get notified about relevant tenders
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors inline-flex items-center gap-2"
              >
                <Plus size={20} />
                Create Your First Alert
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                          {alert.name}
                        </h3>
                        {alert.is_active ? (
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full flex items-center gap-1">
                            <CheckCircle size={12} />
                            Active
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                            Inactive
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Created {new Date(alert.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => toggleAlert(alert.id, alert.is_active)}
                        className={`px-3 py-1 text-sm rounded ${
                          alert.is_active
                            ? 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                            : 'bg-green-600 hover:bg-green-700 text-white'
                        } transition-colors`}
                      >
                        {alert.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                      <button
                        className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                        title="Edit alert"
                      >
                        <Edit2 size={18} />
                      </button>
                      <button
                        onClick={() => deleteAlert(alert.id)}
                        className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="Delete alert"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {alert.keywords.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Keywords
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {alert.keywords.map((keyword, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {alert.category_filter && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Category
                          </h4>
                          <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                            {alert.category_filter}
                          </span>
                        </div>
                      )}

                      {alert.location_filter && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Location
                          </h4>
                          <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                            {alert.location_filter}
                          </span>
                        </div>
                      )}
                    </div>

                    {(alert.min_budget || alert.max_budget) && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Budget Range
                        </h4>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {alert.min_budget ? `$${alert.min_budget.toLocaleString()}` : 'Any'} - {alert.max_budget ? `$${alert.max_budget.toLocaleString()}` : 'Any'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Create Alert Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between sticky top-0 bg-white dark:bg-gray-800">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Create New Alert
              </h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={createAlert} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Alert Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="e.g., IT Infrastructure Tenders"
                  required
                  minLength={3}
                  maxLength={200}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Keywords (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.keywords}
                  onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="e.g., software, cloud, infrastructure"
                />
                <p className="text-xs text-gray-500 mt-1">Separate keywords with commas</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Category
                  </label>
                  <input
                    type="text"
                    value={formData.category_filter}
                    onChange={(e) => setFormData({ ...formData, category_filter: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="e.g., IT Services"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Location
                  </label>
                  <input
                    type="text"
                    value={formData.location_filter}
                    onChange={(e) => setFormData({ ...formData, location_filter: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="e.g., New York"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Minimum Budget ($)
                  </label>
                  <input
                    type="number"
                    value={formData.min_budget}
                    onChange={(e) => setFormData({ ...formData, min_budget: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="0"
                    min="0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Maximum Budget ($)
                  </label>
                  <input
                    type="number"
                    value={formData.max_budget}
                    onChange={(e) => setFormData({ ...formData, max_budget: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="No limit"
                    min="0"
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={submitting}
                >
                  {submitting ? 'Creating...' : 'Create Alert'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
