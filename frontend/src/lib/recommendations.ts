/**
 * Recommendations API Client
 * AI-powered tender recommendations using BGE-M3
 */

import axios from 'axios';
import {
  RecommendationResponse,
  RecommendationFilters,
  SimilarTendersResponse,
  FeedbackRequest,
  FeedbackResponse,
  RecommendationStats,
} from '@/types/recommendation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Get authentication token from localStorage
 */
function getAuthHeaders() {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
  return {};
}

/**
 * Get personalized tender recommendations
 *
 * @param filters - Filter options (limit, min_score, days_ahead, etc.)
 * @returns RecommendationResponse with matched tenders and scores
 */
export async function getRecommendations(
  filters: RecommendationFilters = {}
): Promise<RecommendationResponse> {
  const {
    limit = 20,
    min_score,
    days_ahead = 7,
    sectors,
    regions,
  } = filters;

  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  if (min_score !== undefined) params.append('min_score', min_score.toString());
  params.append('days_ahead', days_ahead.toString());
  if (sectors && sectors.length > 0) {
    sectors.forEach(s => params.append('sectors', s));
  }
  if (regions && regions.length > 0) {
    regions.forEach(r => params.append('regions', r));
  }

  const response = await axios.get<RecommendationResponse>(
    `${API_URL}/recommendations?${params.toString()}`,
    { headers: getAuthHeaders() }
  );

  return response.data;
}

/**
 * Get similar tenders based on vector similarity
 *
 * @param tenderId - Reference tender ID
 * @param limit - Max number of similar tenders to return
 * @returns SimilarTendersResponse with similar tenders
 */
export async function getSimilarTenders(
  tenderId: string,
  limit: number = 10
): Promise<SimilarTendersResponse> {
  const response = await axios.get<SimilarTendersResponse>(
    `${API_URL}/recommendations/tenders/${tenderId}/similar?limit=${limit}`,
    { headers: getAuthHeaders() }
  );

  return response.data;
}

/**
 * Track user interaction with a tender (feedback)
 *
 * @param tenderId - Tender ID
 * @param feedback - Interaction details (type, reason, time spent)
 * @returns FeedbackResponse with success status
 */
export async function submitFeedback(
  tenderId: string,
  feedback: FeedbackRequest
): Promise<FeedbackResponse> {
  const response = await axios.post<FeedbackResponse>(
    `${API_URL}/recommendations/feedback/${tenderId}`,
    feedback,
    { headers: getAuthHeaders() }
  );

  return response.data;
}

/**
 * Refresh company profile embedding
 * Triggers regeneration of the profile's vector embedding
 *
 * @returns Success message
 */
export async function refreshProfileEmbedding(): Promise<{ message: string }> {
  const response = await axios.post<{ message: string }>(
    `${API_URL}/recommendations/refresh-profile-embedding`,
    {},
    { headers: getAuthHeaders() }
  );

  return response.data;
}

/**
 * Get recommendation statistics for current user
 * Mock implementation - replace with actual API when available
 *
 * @returns RecommendationStats
 */
export async function getRecommendationStats(): Promise<RecommendationStats> {
  // TODO: Implement actual endpoint when available
  // For now, return mock data
  return {
    total_recommendations: 0,
    avg_match_score: 0,
    saved_count: 0,
    dismissed_count: 0,
    applied_count: 0,
    profile_completion: 0,
  };
}

/**
 * Recommendation API Client Object
 * Provides all recommendation-related API calls
 */
export const recommendationsApi = {
  getRecommendations,
  getSimilarTenders,
  submitFeedback,
  refreshProfileEmbedding,
  getRecommendationStats,
};

export default recommendationsApi;
