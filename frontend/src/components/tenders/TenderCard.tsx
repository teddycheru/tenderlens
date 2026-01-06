'use client'

import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { Calendar, DollarSign, MapPin, Tag, Sparkles } from 'lucide-react'
import type { Tender } from '@/types/tender'
import MatchScore from '@/components/recommendations/MatchScore'

interface TenderCardProps {
  tender: Tender
  matchScore?: number
}

export function TenderCard({ tender, matchScore }: TenderCardProps) {
  const daysUntilDeadline = tender.deadline ? formatDistanceToNow(new Date(tender.deadline), { addSuffix: true }) : 'No deadline'
  const isExpiringSoon = tender.deadline ? new Date(tender.deadline).getTime() - Date.now() < 7 * 24 * 60 * 60 * 1000 : false

  // Use AI summary if available, otherwise use description
  // Don't auto-generate quick scan on cards - it requires auth and causes latency
  // Truncate description to 200 characters for card preview
  const truncateText = (text: string | undefined, maxLength: number = 200): string => {
    if (!text) return "Click to view tender details"
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength).trim() + "..."
  }

  const displayText = tender.ai_summary || truncateText(tender.description)

  return (
    <Link href={`/tenders/${tender.id}`}>
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex-1">
            {tender.title}
          </h3>
          <div className="flex items-center gap-2">
            {matchScore !== undefined && (
              <MatchScore score={matchScore} size="sm" showLabel={false} />
            )}
            {!tender.is_active && (
              <span className="px-2 py-1 bg-gray-200 text-gray-600 text-xs rounded">
                Closed
              </span>
            )}
          </div>
        </div>

        {/* AI Badge if processed */}
        {tender.ai_processed && (
          <div className="flex items-center gap-1 mb-2">
            <Sparkles size={14} className="text-yellow-500" />
            <span className="text-xs font-medium text-yellow-600 dark:text-yellow-400">
              AI Analyzed
            </span>
          </div>
        )}

        <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-4">
          {displayText}
        </p>

        <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4">
          {tender.category && (
            <div className="flex items-center gap-1">
              <Tag size={16} />
              <span>{tender.category}</span>
            </div>
          )}
          {tender.region && (
            <div className="flex items-center gap-1">
              <MapPin size={16} />
              <span>{tender.region}</span>
            </div>
          )}
          {tender.budget && (
            <div className="flex items-center gap-1">
              <DollarSign size={16} />
              <span>${tender.budget.toLocaleString()}</span>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-1 text-sm">
            <Calendar size={16} className={isExpiringSoon ? 'text-red-500' : 'text-gray-500'} />
            <span className={isExpiringSoon ? 'text-red-500 font-medium' : 'text-gray-500'}>
              Closes {daysUntilDeadline}
            </span>
          </div>
          {tender.organization && (
            <span className="text-xs text-gray-500">{tender.organization}</span>
          )}
        </div>
      </div>
    </Link>
  )
}
