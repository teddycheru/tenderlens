/**
 * AI-Powered Recommendation Types (BGE-M3)
 * Updated: January 1, 2026
 */

/**
 * Match reason explaining why a tender was recommended
 */
export interface MatchReason {
  type: 'semantic_match' | 'sector_match' | 'subsector_match' | 'keyword_match' | 'region_match' | 'budget_match' | 'urgency';
  category: string;
  reason: string;
  weight: number;
}

/**
 * Tender with full details
 */
export interface Tender {
  id: string;
  title: string;
  description?: string;
  clean_description?: string;
  ai_summary?: string;
  category?: string;
  region?: string;
  budget?: number;
  budget_currency?: string;
  deadline?: string;
  language?: string;
  source?: string;
  source_url?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

/**
 * Detailed score breakdown for a tender recommendation
 */
export interface ScoreBreakdown {
  rule_score: number;
  semantic_score: number;
  popularity_score?: number;
  category?: {
    matched: boolean;
    points: number;
    type: string;
  };
  region?: {
    matched: boolean;
    points: number;
    value: string;
  };
  budget?: {
    matched: boolean;
    points: number;
    value?: number;
  };
  keywords?: {
    matched: string[];
    points: number;
  };
  certifications?: {
    matched: string[];
    points: number;
  };
  language?: {
    matched: boolean;
    points: number;
  };
  deadline?: {
    matched: boolean;
    points: number;
    days: number;
  };
}

/**
 * Recommended tender with AI match score and reasons
 */
export interface TenderRecommendation {
  tender: Tender;
  match_score: number; // 0-100
  match_reasons: MatchReason[];
  semantic_similarity: number; // 0-1
  days_until_deadline: number;
}

/**
 * Response from GET /recommendations endpoint
 */
export interface RecommendationResponse {
  recommendations: TenderRecommendation[];
  total_count: number;
  profile_id: string;
  profile_completion: number; // 0-100
  filters_applied?: RecommendationFilters;
  generated_at: string;
}

/**
 * Similar tender result
 */
export interface SimilarTender {
  tender: Tender;
  similarity_score: number; // 0-100
  common_keywords: string[];
}

/**
 * Response from GET /tenders/{id}/similar endpoint
 */
export interface SimilarTendersResponse {
  similar_tenders: SimilarTender[];
  reference_tender: Tender;
  total: number;
}

/**
 * User interaction types for feedback tracking
 */
export type InteractionType = 'view' | 'save' | 'dismiss' | 'apply' | 'rate_positive' | 'rate_negative';

/**
 * Feedback request body for POST /feedback/{tender_id}
 */
export interface FeedbackRequest {
  interaction_type: InteractionType;
  feedback_reason?: string;
  time_spent_seconds?: number;
}

/**
 * Feedback response
 */
export interface FeedbackResponse {
  success: boolean;
  interaction_id: string;
  message: string;
}

/**
 * Filter parameters for recommendations
 */
export interface RecommendationFilters {
  limit?: number; // Default: 20, Max: 100
  min_score?: number; // Default: 0, Range: 0-100
  days_ahead?: number; // Default: 7, Range: 1-90
  sectors?: string[];
  regions?: string[];
}

/**
 * Recommendation statistics
 */
export interface RecommendationStats {
  total_recommendations: number;
  avg_match_score: number;
  saved_count: number;
  dismissed_count: number;
  applied_count: number;
  profile_completion: number;
}

/**
 * Constants for UI display
 */
export const MATCH_SCORE_THRESHOLDS = {
  EXCELLENT: 80,
  GOOD: 60,
  FAIR: 40,
  POOR: 20,
} as const;

export const MATCH_SCORE_COLORS = {
  EXCELLENT: 'text-green-600 bg-green-50 border-green-200',
  GOOD: 'text-blue-600 bg-blue-50 border-blue-200',
  FAIR: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  POOR: 'text-gray-600 bg-gray-50 border-gray-200',
} as const;

export const INTERACTION_LABELS = {
  view: 'Viewed',
  save: 'Saved',
  dismiss: 'Dismissed',
  apply: 'Applied',
  rate_positive: 'Liked',
  rate_negative: 'Disliked',
} as const;

export const REASON_TYPE_ICONS = {
  semantic_match: '🧠',
  sector_match: '🏢',
  subsector_match: '🎯',
  keyword_match: '🔑',
  region_match: '📍',
  budget_match: '💰',
  urgency: '⚡',
} as const;

export const REASON_TYPE_LABELS = {
  semantic_match: 'Semantic Match',
  sector_match: 'Sector Match',
  subsector_match: 'Specialization',
  keyword_match: 'Keyword Match',
  region_match: 'Region Match',
  budget_match: 'Budget Fit',
  urgency: 'Urgent Deadline',
} as const;

/**
 * Helper functions
 */
export function getScoreColor(score: number): string {
  if (score >= MATCH_SCORE_THRESHOLDS.EXCELLENT) return MATCH_SCORE_COLORS.EXCELLENT;
  if (score >= MATCH_SCORE_THRESHOLDS.GOOD) return MATCH_SCORE_COLORS.GOOD;
  if (score >= MATCH_SCORE_THRESHOLDS.FAIR) return MATCH_SCORE_COLORS.FAIR;
  return MATCH_SCORE_COLORS.POOR;
}

export function getScoreLabel(score: number): string {
  if (score >= MATCH_SCORE_THRESHOLDS.EXCELLENT) return 'Excellent Match';
  if (score >= MATCH_SCORE_THRESHOLDS.GOOD) return 'Good Match';
  if (score >= MATCH_SCORE_THRESHOLDS.FAIR) return 'Fair Match';
  return 'Low Match';
}

export function getScoreBadgeClass(score: number): string {
  const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border';
  const colorClass = getScoreColor(score);
  return `${baseClasses} ${colorClass}`;
}
