'use client'

import { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, PieChart, Activity } from 'lucide-react'
import { analyticsApi } from '@/lib/analytics'

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [summaryStats, setSummaryStats] = useState({
    total_tenders: 0,
    upcoming_tenders: 0,
    recent_tenders: 0,
    average_budget: 0,
  })
  const [categoryData, setCategoryData] = useState<any>({})
  const [regionalData, setRegionalData] = useState<any>({})

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      setError(null)

      const [summary, categories, regions] = await Promise.all([
        analyticsApi.getSummaryStats(),
        fetch('http://localhost:8000/api/v1/analytics/category-distribution').then(r => r.json()),
        fetch('http://localhost:8000/api/v1/analytics/regional-distribution').then(r => r.json()),
      ])

      setSummaryStats(summary)
      setCategoryData(categories)
      setRegionalData(regions)
    } catch (err: any) {
      console.error('Error fetching analytics:', err)
      setError(err.response?.data?.detail || 'Failed to fetch analytics')
    } finally {
      setLoading(false)
    }
  }

  const topCategories = Object.entries(categoryData.categories || {})
    .sort(([, a]: any, [, b]: any) => b - a)
    .slice(0, 10)

  const topRegions = Object.entries(regionalData.regions || {})
    .sort(([, a]: any, [, b]: any) => b - a)
    .slice(0, 10)

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Analytics Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Insights and trends from tender data
        </p>
      </div>

      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Total Tenders
                  </p>
                  <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">
                    {summaryStats.total_tenders.toLocaleString()}
                  </p>
                </div>
                <div className="bg-blue-500 p-3 rounded-lg">
                  <BarChart3 size={24} className="text-white" />
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Recent (7 days)
                  </p>
                  <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">
                    {summaryStats.recent_tenders.toLocaleString()}
                  </p>
                </div>
                <div className="bg-purple-500 p-3 rounded-lg">
                  <Activity size={24} className="text-white" />
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Upcoming (30 days)
                  </p>
                  <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">
                    {summaryStats.upcoming_tenders.toLocaleString()}
                  </p>
                </div>
                <div className="bg-orange-500 p-3 rounded-lg">
                  <TrendingUp size={24} className="text-white" />
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Avg Budget
                  </p>
                  <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">
                    {summaryStats.average_budget > 0
                      ? `$${Math.round(summaryStats.average_budget / 1000)}K`
                      : 'N/A'}
                  </p>
                </div>
                <div className="bg-green-500 p-3 rounded-lg">
                  <PieChart size={24} className="text-white" />
                </div>
              </div>
            </div>
          </div>

          {/* Category Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                <BarChart3 size={24} className="text-blue-600" />
                Top Categories
              </h2>
              {topCategories.length > 0 ? (
                <div className="space-y-3">
                  {topCategories.map(([category, count]: any, index) => (
                    <div key={category}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {category}
                        </span>
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">
                          {count}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{
                            width: `${topCategories.length > 0 ? (count / (topCategories[0][1] as number)) * 100 : 0}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center py-8 text-gray-500">No category data available</p>
              )}
            </div>

            {/* Regional Distribution */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                <PieChart size={24} className="text-purple-600" />
                Top Regions
              </h2>
              {topRegions.length > 0 ? (
                <div className="space-y-3">
                  {topRegions.map(([region, count]: any, index) => (
                    <div key={region}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {region || 'Unknown'}
                        </span>
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">
                          {count}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-purple-600 h-2 rounded-full transition-all"
                          style={{
                            width: `${topRegions.length > 0 ? (count / (topRegions[0][1] as number)) * 100 : 0}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center py-8 text-gray-500">No regional data available</p>
              )}
            </div>
          </div>

          {/* Additional Insights */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
              <TrendingUp size={24} className="text-green-600" />
              Key Insights
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h3 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">
                  Most Active Category
                </h3>
                <p className="text-sm text-blue-800 dark:text-blue-300">
                  {topCategories.length > 0
                    ? `${topCategories[0][0]} with ${topCategories[0][1]} tenders`
                    : 'No data available'}
                </p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <h3 className="font-semibold text-purple-900 dark:text-purple-200 mb-2">
                  Most Active Region
                </h3>
                <p className="text-sm text-purple-800 dark:text-purple-300">
                  {topRegions.length > 0
                    ? `${topRegions[0][0] || 'Unknown'} with ${topRegions[0][1]} tenders`
                    : 'No data available'}
                </p>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <h3 className="font-semibold text-green-900 dark:text-green-200 mb-2">
                  Activity Rate
                </h3>
                <p className="text-sm text-green-800 dark:text-green-300">
                  {summaryStats.total_tenders > 0
                    ? `${((summaryStats.recent_tenders / summaryStats.total_tenders) * 100).toFixed(1)}% added in last 7 days`
                    : 'No data available'}
                </p>
              </div>
              <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <h3 className="font-semibold text-orange-900 dark:text-orange-200 mb-2">
                  Opportunity Window
                </h3>
                <p className="text-sm text-orange-800 dark:text-orange-300">
                  {summaryStats.upcoming_tenders > 0
                    ? `${summaryStats.upcoming_tenders} tenders closing in next 30 days`
                    : 'No upcoming deadlines'}
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
