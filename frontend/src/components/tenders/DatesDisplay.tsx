'use client'

import { Calendar, Clock } from 'lucide-react'
import { formatDistanceToNow, format, isPast } from 'date-fns'
import type { DatesData } from '@/types/tender'

interface DatesDisplayProps {
  dates?: DatesData
  deadline?: string
}

export function DatesDisplay({ dates, deadline }: DatesDisplayProps) {
  const closingDate = dates?.closing_date || deadline
  const publishedDate = dates?.published_date

  if (!closingDate && !publishedDate) return null

  const parseDate = (dateStr?: string) => {
    if (!dateStr) return null
    try {
      const date = new Date(dateStr)
      // Check if date is valid
      if (isNaN(date.getTime())) return null
      return date
    } catch {
      return null
    }
  }

  const closingDateTime = parseDate(closingDate)
  const publishedDateTime = parseDate(publishedDate)

  const isClosingSoon =
    closingDateTime && !isPast(closingDateTime) && Date.now() + 7 * 24 * 60 * 60 * 1000 > closingDateTime.getTime()
  const isExpired = closingDateTime && isPast(closingDateTime)

  return (
    <div className="bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <div className="p-2 bg-red-100 dark:bg-red-900/40 rounded-lg">
          <Calendar size={24} className="text-red-600 dark:text-red-400" />
        </div>
        Important Dates
      </h3>

      <div className="space-y-3">
        {publishedDateTime && (
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium mb-1">Published Date</p>
            <div className="flex items-center gap-2">
              <Clock size={16} className="text-gray-500 dark:text-gray-400" />
              <span className="text-sm text-gray-700 dark:text-gray-300">{format(publishedDateTime, 'PPP p')}</span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              {formatDistanceToNow(publishedDateTime, { addSuffix: true })}
            </p>
          </div>
        )}

        {closingDateTime && (
          <div
            className={`p-4 rounded-lg border-2 ${
              isExpired
                ? 'bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700'
                : isClosingSoon
                  ? 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
                  : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className={`text-sm font-medium mb-1 ${isExpired ? 'text-gray-600 dark:text-gray-400' : isClosingSoon ? 'text-red-700 dark:text-red-300' : 'text-gray-600 dark:text-gray-400'}`}>
                  Closing Deadline
                </p>
                <div className="flex items-center gap-2">
                  <Calendar size={16} className={isExpired ? 'text-gray-500 dark:text-gray-400' : isClosingSoon ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-400'} />
                  <span className={`text-sm font-semibold ${isExpired ? 'text-gray-700 dark:text-gray-300 line-through' : isClosingSoon ? 'text-red-700 dark:text-red-300' : 'text-gray-700 dark:text-gray-300'}`}>
                    {format(closingDateTime, 'PPP p')}
                  </span>
                </div>
              </div>
              {isExpired && (
                <span className="px-2 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs font-semibold rounded">
                  Expired
                </span>
              )}
              {isClosingSoon && (
                <span className="px-2 py-1 bg-red-200 dark:bg-red-700 text-red-700 dark:text-red-200 text-xs font-semibold rounded animate-pulse">
                  Closing Soon
                </span>
              )}
            </div>

            {!isExpired && closingDateTime && (
              <p
                className={`text-xs mt-2 ${isClosingSoon ? 'text-red-600 dark:text-red-400 font-semibold' : 'text-gray-500 dark:text-gray-500'}`}
              >
                {formatDistanceToNow(closingDateTime, { addSuffix: true })}
              </p>
            )}
          </div>
        )}

        {dates?.closing_date_original && (
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium mb-1">Original Format</p>
            <p className="text-sm text-gray-700 dark:text-gray-300 italic">{dates.closing_date_original}</p>
          </div>
        )}
      </div>
    </div>
  )
}
