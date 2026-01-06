/**
 * React hooks for AI-powered tender recommendations
 */

import { useState, useEffect, useCallback } from 'react';
import {
  RecommendationResponse,
  RecommendationFilters,
  TenderRecommendation,
  SimilarTendersResponse,
  FeedbackRequest,
  InteractionType,
} from '@/types/recommendation';
import recommendationsApi from '@/lib/recommendations';

/**
 * Hook for fetching and managing recommendations
 *
 * @param initialFilters - Initial filter parameters
 * @param autoFetch - Whether to fetch immediately on mount
 * @returns Recommendations data, loading state, and refetch function
 */
export function useRecommendations(
  initialFilters: RecommendationFilters = {},
  autoFetch: boolean = true
) {
  const [data, setData] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [filters, setFilters] = useState<RecommendationFilters>(initialFilters);

  const fetchRecommendations = useCallback(
    async (newFilters?: RecommendationFilters) => {
      const filtersToUse = newFilters || filters;
      setLoading(true);
      setError(null);

      try {
        const response = await recommendationsApi.getRecommendations(filtersToUse);
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch recommendations'));
      } finally {
        setLoading(false);
      }
    },
    [filters]
  );

  useEffect(() => {
    if (autoFetch) {
      fetchRecommendations();
    }
  }, [autoFetch, fetchRecommendations]);

  const updateFilters = useCallback((newFilters: Partial<RecommendationFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const refetch = useCallback(() => {
    fetchRecommendations(filters);
  }, [filters, fetchRecommendations]);

  return {
    recommendations: data?.recommendations || [],
    total: data?.total_count || 0,
    profileCompletion: data?.profile_completion || 0,
    filtersApplied: data?.filters_applied || {},
    loading,
    error,
    filters,
    updateFilters,
    refetch,
  };
}

/**
 * Hook for fetching similar tenders
 *
 * @param tenderId - Reference tender ID (null to skip fetching)
 * @param limit - Max number of similar tenders
 * @returns Similar tenders data and loading state
 */
export function useSimilarTenders(tenderId: string | null, limit: number = 10) {
  const [data, setData] = useState<SimilarTendersResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!tenderId) {
      setData(null);
      return;
    }

    setLoading(true);
    setError(null);

    recommendationsApi
      .getSimilarTenders(tenderId, limit)
      .then(response => {
        setData(response);
      })
      .catch(err => {
        setError(err instanceof Error ? err : new Error('Failed to fetch similar tenders'));
      })
      .finally(() => {
        setLoading(false);
      });
  }, [tenderId, limit]);

  return {
    similarTenders: data?.similar_tenders || [],
    referenceTender: data?.reference_tender || null,
    total: data?.total || 0,
    loading,
    error,
  };
}

/**
 * Hook for tracking user interactions (feedback)
 *
 * @returns Submit feedback function and loading state
 */
export function useFeedback() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const submitFeedback = useCallback(
    async (
      tenderId: string,
      interactionType: InteractionType,
      feedbackReason?: string,
      timeSpentSeconds?: number
    ) => {
      setLoading(true);
      setError(null);

      const feedback: FeedbackRequest = {
        interaction_type: interactionType,
        feedback_reason: feedbackReason,
        time_spent_seconds: timeSpentSeconds,
      };

      try {
        const response = await recommendationsApi.submitFeedback(tenderId, feedback);
        return response;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to submit feedback');
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    submitFeedback,
    loading,
    error,
  };
}

/**
 * Hook for managing saved/dismissed tenders locally
 *
 * @returns Saved and dismissed tender IDs with management functions
 */
export function useTenderActions() {
  const [savedTenders, setSavedTenders] = useState<Set<string>>(new Set());
  const [dismissedTenders, setDismissedTenders] = useState<Set<string>>(new Set());
  const { submitFeedback } = useFeedback();

  const saveTender = useCallback(
    async (tenderId: string) => {
      setSavedTenders(prev => new Set(prev).add(tenderId));
      try {
        await submitFeedback(tenderId, 'save');
      } catch (error) {
        setSavedTenders(prev => {
          const next = new Set(prev);
          next.delete(tenderId);
          return next;
        });
        throw error;
      }
    },
    [submitFeedback]
  );

  const unsaveTender = useCallback((tenderId: string) => {
    setSavedTenders(prev => {
      const next = new Set(prev);
      next.delete(tenderId);
      return next;
    });
  }, []);

  const dismissTender = useCallback(
    async (tenderId: string, reason?: string) => {
      setDismissedTenders(prev => new Set(prev).add(tenderId));
      try {
        await submitFeedback(tenderId, 'dismiss', reason);
      } catch (error) {
        setDismissedTenders(prev => {
          const next = new Set(prev);
          next.delete(tenderId);
          return next;
        });
        throw error;
      }
    },
    [submitFeedback]
  );

  const markAsViewed = useCallback(
    async (tenderId: string, timeSpent?: number) => {
      try {
        await submitFeedback(tenderId, 'view', undefined, timeSpent);
      } catch (error) {
        console.error('Failed to track view:', error);
      }
    },
    [submitFeedback]
  );

  const markAsApplied = useCallback(
    async (tenderId: string) => {
      try {
        await submitFeedback(tenderId, 'apply');
      } catch (error) {
        console.error('Failed to track application:', error);
        throw error;
      }
    },
    [submitFeedback]
  );

  return {
    savedTenders,
    dismissedTenders,
    saveTender,
    unsaveTender,
    dismissTender,
    markAsViewed,
    markAsApplied,
    isSaved: (tenderId: string) => savedTenders.has(tenderId),
    isDismissed: (tenderId: string) => dismissedTenders.has(tenderId),
  };
}

/**
 * Hook for refreshing profile embedding
 *
 * @returns Refresh function and loading state
 */
export function useProfileEmbeddingRefresh() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await recommendationsApi.refreshProfileEmbedding();
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to refresh profile embedding');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    refresh,
    loading,
    error,
  };
}
