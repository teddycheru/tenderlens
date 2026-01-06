/**
 * Types for user interaction tracking and learning system
 */

export type InteractionType =
  | 'view'
  | 'save'
  | 'apply'
  | 'dismiss'
  | 'rate_positive'
  | 'rate_negative';

export interface InteractionCreate {
  tender_id: string;
  interaction_type: InteractionType;
  time_spent_seconds?: number;
  feedback_reason?: string;
}

export interface InteractionResponse {
  id: string;
  user_id: string;
  tender_id: string;
  interaction_type: InteractionType;
  interaction_weight: number;
  time_spent_seconds?: number;
  match_score_at_time?: number;
  feedback_reason?: string;
  created_at: string;
}

export interface InteractionStats {
  total_interactions: number;
  views: number;
  saves: number;
  applies: number;
  positive_ratings: number;
  negative_ratings: number;
  dismissals: number;
}

export interface InteractionBatchCreate {
  interactions: InteractionCreate[];
}
