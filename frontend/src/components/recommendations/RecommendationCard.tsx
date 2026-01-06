/**
 * RecommendationCard Component
 * Displays a single tender recommendation with match score and reasons
 */

import React, { useState } from 'react';
import Link from 'next/link';
import { TenderRecommendation } from '@/types/recommendation';
import MatchScore from './MatchScore';
import MatchReasons, { MatchReasonsSummary } from './MatchReasons';
import FeedbackButtons, { QuickActionButtons } from './FeedbackButtons';

interface RecommendationCardProps {
  recommendation: TenderRecommendation;
  variant?: 'compact' | 'detailed';
  showFeedbackButtons?: boolean;
  onSave?: () => void;
  onDismiss?: () => void;
  onApply?: () => void;
  className?: string;
}

export default function RecommendationCard({
  recommendation,
  variant = 'detailed',
  showFeedbackButtons = true,
  onSave,
  onDismiss,
  onApply,
  className = '',
}: RecommendationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { tender, match_score, match_reasons, days_until_deadline } = recommendation;

  const isUrgent = days_until_deadline <= 7;
  const isExpired = days_until_deadline < 0;

  return (
    <div
      className={`bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow ${className}`}
    >
      {/* Card Header */}
      <div className="p-5">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="flex-1 min-w-0">
            <Link
              href={`/dashboard/tenders/${tender.id}`}
              className="text-lg font-semibold text-gray-900 hover:text-blue-600 line-clamp-2"
            >
              {tender.title}
            </Link>
          </div>

          <div className="flex-shrink-0">
            <MatchScore score={match_score} size="md" showLabel={false} />
          </div>
        </div>

        {/* Tender Metadata */}
        <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 mb-4">
          {/* Deadline */}
          {tender.deadline && (
            <div
              className={`flex items-center gap-1.5 ${
                isExpired
                  ? 'text-red-600'
                  : isUrgent
                  ? 'text-orange-600 font-medium'
                  : ''
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <span>
                {isExpired
                  ? 'Expired'
                  : days_until_deadline === 0
                  ? 'Due today'
                  : days_until_deadline === 1
                  ? 'Due tomorrow'
                  : `${days_until_deadline} days left`}
              </span>
              {isUrgent && !isExpired && <span className="text-orange-600">⚡</span>}
            </div>
          )}

          {/* Budget */}
          {tender.budget && (
            <div className="flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>
                {tender.budget_currency} {tender.budget.toLocaleString()}
              </span>
            </div>
          )}

          {/* Region */}
          {tender.region && (
            <div className="flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span>{tender.region}</span>
            </div>
          )}

          {/* Category */}
          {tender.category && (
            <div className="flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                />
              </svg>
              <span>{tender.category}</span>
            </div>
          )}
        </div>

        {/* Description */}
        {variant === 'detailed' && (
          <div className="mb-4">
            {tender.ai_summary ? (
              <p className="text-sm text-gray-700 line-clamp-3">
                {tender.ai_summary}
              </p>
            ) : tender.clean_description ? (
              <p className="text-sm text-gray-700 line-clamp-3">
                {tender.clean_description}
              </p>
            ) : tender.description ? (
              <p className="text-sm text-gray-700 line-clamp-3">
                {tender.description}
              </p>
            ) : null}
          </div>
        )}

        {/* Match Reasons Summary */}
        {!isExpanded && match_reasons.length > 0 && (
          <div className="mb-4">
            <MatchReasonsSummary reasons={match_reasons} />
          </div>
        )}

        {/* Expanded Match Reasons */}
        {isExpanded && match_reasons.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-2">
              Why this matches ({match_reasons.length} reasons)
            </h4>
            <MatchReasons
              reasons={match_reasons}
              variant="detailed"
              maxVisible={5}
              showWeights={true}
            />
          </div>
        )}

        {/* Expand/Collapse Button */}
        {match_reasons.length > 0 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium mb-4"
          >
            {isExpanded ? 'Show less' : 'Show match details'}
          </button>
        )}

        {/* Actions */}
        {showFeedbackButtons && (
          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            <div className="flex gap-2">
              {tender.source_url && (
                <a
                  href={tender.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-700 hover:text-blue-600 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                  View source
                </a>
              )}
            </div>

            <FeedbackButtons
              tenderId={tender.id}
              layout="horizontal"
              size="sm"
              showLabels={variant === 'detailed'}
              onSave={onSave}
              onDismiss={onDismiss}
              onApply={onApply}
            />
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Compact card variant for list views
 */
export function RecommendationCardCompact({
  recommendation,
  onSave,
  onDismiss,
  className = '',
}: {
  recommendation: TenderRecommendation;
  onSave?: () => void;
  onDismiss?: () => void;
  className?: string;
}) {
  const { tender, match_score, days_until_deadline } = recommendation;
  const isUrgent = days_until_deadline <= 7;

  return (
    <div
      className={`bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <Link
            href={`/dashboard/tenders/${tender.id}`}
            className="text-base font-semibold text-gray-900 hover:text-blue-600 line-clamp-2 mb-2"
          >
            {tender.title}
          </Link>

          <div className="flex flex-wrap items-center gap-3 text-xs text-gray-600 mb-3">
            {tender.deadline && (
              <span className={isUrgent ? 'text-orange-600 font-medium' : ''}>
                {days_until_deadline} days left
                {isUrgent && ' ⚡'}
              </span>
            )}
            {tender.region && <span>📍 {tender.region}</span>}
            {tender.category && <span>🏢 {tender.category}</span>}
          </div>
        </div>

        <div className="flex flex-col items-end gap-2">
          <MatchScore score={match_score} size="sm" showLabel={false} />
          <QuickActionButtons
            tenderId={tender.id}
            onSave={onSave}
            onDismiss={onDismiss}
          />
        </div>
      </div>
    </div>
  );
}

/**
 * Skeleton loading card
 */
export function RecommendationCardSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-5 ${className}`}>
      <div className="animate-pulse">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="flex-1 space-y-2">
            <div className="h-6 bg-gray-200 rounded w-3/4"></div>
            <div className="h-6 bg-gray-200 rounded w-1/2"></div>
          </div>
          <div className="h-8 w-16 bg-gray-200 rounded-full"></div>
        </div>

        <div className="flex gap-3 mb-4">
          <div className="h-4 w-24 bg-gray-200 rounded"></div>
          <div className="h-4 w-32 bg-gray-200 rounded"></div>
          <div className="h-4 w-20 bg-gray-200 rounded"></div>
        </div>

        <div className="space-y-2 mb-4">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>

        <div className="flex gap-2">
          <div className="h-9 w-24 bg-gray-200 rounded-lg"></div>
          <div className="h-9 w-24 bg-gray-200 rounded-lg"></div>
          <div className="h-9 w-24 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    </div>
  );
}
