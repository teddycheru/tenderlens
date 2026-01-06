'use client'

import { useState, useEffect } from 'react'
import { FileText, TrendingUp, Clock, AlertCircle } from 'lucide-react'
import { analyticsApi } from '@/lib/analytics'

export default function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const [statsData, setStatsData] = useState({
    total_tenders: 0,
    upcoming_tenders: 0,
    recent_tenders: 0,
    average_budget: 0,
  })

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const data = await analyticsApi.getSummaryStats()
        setStatsData(data)
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const stats = [
    {
      name: 'Total Tenders',
      value: statsData.total_tenders.toString(),
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      name: 'Recent Tenders',
      value: statsData.recent_tenders.toString(),
      icon: TrendingUp,
      color: 'bg-purple-500',
    },
    {
      name: 'Upcoming Deadlines',
      value: statsData.upcoming_tenders.toString(),
      icon: Clock,
      color: 'bg-orange-500',
    },
    {
      name: 'Average Budget',
      value: statsData.average_budget > 0
        ? `$${Math.round(statsData.average_budget).toLocaleString()}`
        : 'N/A',
      icon: AlertCircle,
      color: 'bg-green-500',
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Welcome to your tender management dashboard
        </p>
      </div>

      {!loading && statsData.total_tenders === 0 && (
        <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <p className="text-yellow-800 dark:text-yellow-200 text-sm">
            📊 No tender data available yet. Import sample data to get started using the CSV import script.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {loading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 animate-pulse"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-2"></div>
                    <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
                  </div>
                  <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                </div>
              </div>
            ))}
          </>
        ) : (
          stats.map((stat) => {
            const Icon = stat.icon
            return (
              <div
                key={stat.name}
                className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {stat.name}
                    </p>
                    <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon size={24} className="text-white" />
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Recent Tenders
          </h2>
          <div className="text-center py-8 text-gray-500">
            <FileText size={48} className="mx-auto mb-2 opacity-20" />
            <p>No tenders yet</p>
            <p className="text-sm mt-1">Start by browsing available tenders</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Recent Alerts
          </h2>
          <div className="text-center py-8 text-gray-500">
            <AlertCircle size={48} className="mx-auto mb-2 opacity-20" />
            <p>No alerts configured</p>
            <p className="text-sm mt-1">Create alerts to get notified about new tenders</p>
          </div>
        </div>
      </div>
    </div>
  )
}
