/**
 * RecommendationList Component
 * Displays a list of tender recommendations with filters and controls
 */

import React, { useState } from 'react';
import { useRecommendations } from '@/hooks/useRecommendations';
import { RecommendationFilters } from '@/types/recommendation';
import RecommendationCard, {
  RecommendationCardCompact,
  RecommendationCardSkeleton,
} from './RecommendationCard';

interface RecommendationListProps {
  initialFilters?: RecommendationFilters;
  viewMode?: 'grid' | 'list';
  variant?: 'compact' | 'detailed';
  showFilters?: boolean;
  className?: string;
}

export default function RecommendationList({
  initialFilters = {},
  viewMode = 'list',
  variant = 'detailed',
  showFilters = true,
  className = '',
}: RecommendationListProps) {
  const {
    recommendations,
    total,
    profileCompletion,
    loading,
    error,
    filters,
    updateFilters,
    refetch,
  } = useRecommendations(initialFilters);

  const [localFilters, setLocalFilters] = useState<RecommendationFilters>(initialFilters);

  const handleFilterChange = (newFilters: Partial<RecommendationFilters>) => {
    const updated = { ...localFilters, ...newFilters };
    setLocalFilters(updated);
    updateFilters(updated);
  };

  const handleRefresh = () => {
    refetch();
  };

  return (
    <div className={className}>
      {/* Profile Completion Alert */}
      {profileCompletion < 100 && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-blue-900 mb-1">
                Complete your profile for better recommendations
              </h3>
              <p className="text-sm text-blue-700 mb-2">
                Your profile is {Math.round(profileCompletion)}% complete. Add more details to get
                more accurate tender matches.
              </p>
              <a
                href="/settings"
                className="text-sm font-medium text-blue-600 hover:text-blue-700"
              >
                Complete profile →
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      {showFilters && (
        <RecommendationFiltersBar
          filters={localFilters}
          onFilterChange={handleFilterChange}
          onRefresh={handleRefresh}
          total={total}
          loading={loading}
        />
      )}

      {/* Error State */}
      {error && (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-center">
          <svg
            className="w-12 h-12 text-red-400 mx-auto mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            Failed to load recommendations
          </h3>
          <p className="text-sm text-gray-600 mb-4">{error.message}</p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try again
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && recommendations.length === 0 && (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
              : 'space-y-4'
          }
        >
          {[1, 2, 3, 4].map((i) => (
            <RecommendationCardSkeleton key={i} />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && recommendations.length === 0 && (
        <div className="p-12 bg-gray-50 border border-gray-200 rounded-lg text-center">
          <svg
            className="w-16 h-16 text-gray-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No recommendations found
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            {profileCompletion < 50
              ? 'Complete your company profile to get personalized tender recommendations.'
              : 'Try adjusting your filters or check back later for new tenders.'}
          </p>
          {profileCompletion < 50 ? (
            <a
              href="/dashboard/settings"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Complete profile
            </a>
          ) : (
            <button
              onClick={() => handleFilterChange({ min_score: 0 })}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Clear filters
            </button>
          )}
        </div>
      )}

      {/* Recommendations Grid/List */}
      {!loading && !error && recommendations.length > 0 && (
        <div>
          <div
            className={
              viewMode === 'grid'
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
                : 'space-y-4'
            }
          >
            {recommendations.map((rec) =>
              variant === 'compact' ? (
                <RecommendationCardCompact
                  key={rec.tender.id}
                  recommendation={rec}
                  onSave={handleRefresh}
                  onDismiss={handleRefresh}
                />
              ) : (
                <RecommendationCard
                  key={rec.tender.id}
                  recommendation={rec}
                  variant={variant}
                  onSave={handleRefresh}
                  onDismiss={handleRefresh}
                  onApply={handleRefresh}
                />
              )
            )}
          </div>

          {/* Results Summary */}
          <div className="mt-6 text-center text-sm text-gray-500">
            Showing {recommendations.length} of {total} recommendations
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Filters bar component
 */
function RecommendationFiltersBar({
  filters,
  onFilterChange,
  onRefresh,
  total,
  loading,
}: {
  filters: RecommendationFilters;
  onFilterChange: (filters: Partial<RecommendationFilters>) => void;
  onRefresh: () => void;
  total: number;
  loading: boolean;
}) {
  return (
    <div className="mb-6 p-4 bg-white border border-gray-200 rounded-lg">
      <div className="flex flex-wrap items-center gap-4">
        {/* Min Score Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Min Score:</label>
          <select
            value={filters.min_score || 0}
            onChange={(e) => onFilterChange({ min_score: Number(e.target.value) })}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={0}>All</option>
            <option value={40}>40%+</option>
            <option value={60}>60%+</option>
            <option value={80}>80%+</option>
          </select>
        </div>

        {/* Days Ahead Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Deadline:</label>
          <select
            value={filters.days_ahead || 7}
            onChange={(e) => onFilterChange({ days_ahead: Number(e.target.value) })}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={7}>Next 7 days</option>
            <option value={14}>Next 14 days</option>
            <option value={30}>Next 30 days</option>
            <option value={60}>Next 60 days</option>
            <option value={90}>Next 90 days</option>
          </select>
        </div>

        {/* Limit Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Show:</label>
          <select
            value={filters.limit || 20}
            onChange={(e) => onFilterChange({ limit: Number(e.target.value) })}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={10}>10 results</option>
            <option value={20}>20 results</option>
            <option value={50}>50 results</option>
            <option value={100}>100 results</option>
          </select>
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Results Count */}
        <div className="text-sm text-gray-600">
          {total} {total === 1 ? 'match' : 'matches'}
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={loading}
          className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
          title="Refresh recommendations"
        >
          <svg
            className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

/**
 * Empty state component
 */
export function RecommendationsEmptyState({
  profileCompletion,
  onCompleteProfile,
  onClearFilters,
  className = '',
}: {
  profileCompletion: number;
  onCompleteProfile?: () => void;
  onClearFilters?: () => void;
  className?: string;
}) {
  return (
    <div className={`p-12 bg-gray-50 border border-gray-200 rounded-lg text-center ${className}`}>
      <svg
        className="w-16 h-16 text-gray-400 mx-auto mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">No recommendations yet</h3>
      <p className="text-sm text-gray-600 mb-4">
        {profileCompletion < 50
          ? 'Complete your company profile to get personalized tender recommendations.'
          : 'Check back later for new tender opportunities.'}
      </p>
      {profileCompletion < 50 && (
        <a
          href="/settings"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Complete profile
        </a>
      )}
      {profileCompletion >= 50 && onClearFilters && (
        <button
          onClick={onClearFilters}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Adjust filters
        </button>
      )}
    </div>
  );
}
