'use client'

import { CheckCircle2, Package } from 'lucide-react'
import type { ExtractedData } from '@/types/tender'

interface RequirementsAndSpecsProps {
  extractedData?: ExtractedData
}

export function RequirementsAndSpecs({ extractedData }: RequirementsAndSpecsProps) {
  const requirements = extractedData?.requirements
  const specifications = extractedData?.specifications

  const hasData = (requirements && requirements.length > 0) || (specifications && specifications.length > 0)

  if (!hasData) return null

  return (
    <div className="space-y-6">
      {/* Requirements */}
      {requirements && requirements.length > 0 && (
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/40 rounded-lg">
              <CheckCircle2 size={24} className="text-purple-600 dark:text-purple-400" />
            </div>
            Requirements ({requirements.length})
          </h3>

          <div className="space-y-2">
            {requirements.map((req, idx) => (
              <div key={idx} className="flex gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-shadow">
                <div className="flex-shrink-0 pt-1">
                  <CheckCircle2 size={18} className="text-purple-600 dark:text-purple-400" />
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{req}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Specifications */}
      {specifications && specifications.length > 0 && (
        <div className="bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <div className="p-2 bg-orange-100 dark:bg-orange-900/40 rounded-lg">
              <Package size={24} className="text-orange-600 dark:text-orange-400" />
            </div>
            Specifications ({specifications.length})
          </h3>

          {/* Specifications Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-orange-200 dark:border-orange-800">
                  {specifications[0] && Object.keys(specifications[0]).map((key) => (
                    <th
                      key={key}
                      className="text-left px-4 py-3 font-semibold text-gray-900 dark:text-white bg-orange-100/50 dark:bg-orange-900/30"
                    >
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {specifications.map((spec, idx) => (
                  <tr key={idx} className="border-b border-orange-100 dark:border-orange-900/50 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors">
                    {Object.entries(spec).map(([key, value]) => (
                      <td key={`${idx}-${key}`} className="px-4 py-3 text-gray-700 dark:text-gray-300">
                        {value}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
