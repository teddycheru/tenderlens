/**
 * Types for company tender profile and recommendation system
 * Updated to match backend schema with Ethiopian multi-sector business model
 */

export interface CompanyTenderProfile {
  id: string;
  company_id: string;

  // Tier 1: Critical Fields (Required)
  primary_sector: string;              // For identity/branding only
  active_sectors: string[];            // Actual work sectors (max 5)
  sub_sectors: string[];               // Fine-grained specializations
  preferred_regions: string[];         // Geographic preferences
  keywords: string[];                  // Core capabilities (3-10 keywords)

  // Tier 2: Important Fields (Optional)
  company_size?: string;               // 'startup' | 'small' | 'medium' | 'large'
  years_in_operation?: string;         // '<1' | '1-3' | '3-5' | '5-10' | '10+'
  certifications?: string[];
  budget_min?: number;
  budget_max?: number;
  budget_currency: string;             // Default 'ETB'

  // Tier 3: Learned Preferences (Auto-updated)
  discovered_interests?: string[];     // Sectors discovered through behavior
  preferred_sources?: string[];
  preferred_languages?: string[];
  min_deadline_days?: number;

  // Matching Configuration
  min_match_threshold: number;         // 0-100
  scoring_weights: Record<string, number>;

  // Metadata
  profile_completed: boolean;
  onboarding_step: number;             // 0-2
  interaction_count: number;
  last_interaction_at?: string;
  embedding_updated_at?: string;

  // Computed Properties
  completion_percentage: number;
  is_tier1_complete: boolean;
  is_tier2_complete: boolean;

  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface CompanyProfileCreate {
  // Tier 1 (Required)
  primary_sector: string;
  active_sectors: string[];            // min: 1, max: 5
  sub_sectors: string[];
  preferred_regions: string[];         // min: 1, max: 5
  keywords: string[];                  // min: 3, max: 10

  // Tier 2 (Optional)
  company_size?: string;
  years_in_operation?: string;
  certifications?: string[];
  budget_min?: number;
  budget_max?: number;
  budget_currency?: string;            // Default 'ETB'
}

export interface CompanyProfileCreateStep1 {
  primary_sector: string;
  active_sectors: string[];            // min: 1, max: 5
  sub_sectors: string[];
  preferred_regions: string[];
  keywords: string[];                  // min: 3, max: 10
}

export interface CompanyProfileCreateStep2 {
  company_size?: string;
  years_in_operation?: string;
  certifications?: string[];
  budget_min?: number;
  budget_max?: number;
  budget_currency?: string;
}

export interface CompanyProfileUpdate {
  // All fields optional for partial updates
  primary_sector?: string;
  active_sectors?: string[];
  sub_sectors?: string[];
  preferred_regions?: string[];
  keywords?: string[];
  company_size?: string;
  years_in_operation?: string;
  certifications?: string[];
  budget_min?: number;
  budget_max?: number;
  budget_currency?: string;

  // Allow manual updates to learned preferences
  discovered_interests?: string[];
  preferred_sources?: string[];
  preferred_languages?: string[];
  min_deadline_days?: number;

  // Matching settings
  min_match_threshold?: number;
  scoring_weights?: Record<string, number>;
}

export interface CompanyProfileSummary {
  id: string;
  company_id: string;
  primary_sector: string;
  active_sectors: string[];
  profile_completed: boolean;
  completion_percentage: number;
  created_at: string;
}

export interface ProfileOptions {
  sectors: string[];                   // List of available business sectors
  regions: string[];                   // List of Ethiopian regions
  certifications: string[];            // Common certifications
  company_sizes: string[];             // ['startup', 'small', 'medium', 'large']
  years_options: string[];             // ['<1', '1-3', '3-5', '5-10', '10+']
  keyword_suggestions: Record<string, string[]>;  // Suggestions by sector
}

export interface UserInteraction {
  id: string;
  user_id: string;
  tender_id: string;
  interaction_type: 'view' | 'save' | 'apply' | 'dismiss' | 'rate_positive' | 'rate_negative';
  interaction_weight: number;
  time_spent_seconds?: number;
  match_score_at_time?: number;
  tender_category?: string;
  tender_region?: string;
  tender_budget?: number;
  feedback_reason?: string;
  created_at: string;
}

export interface UserInteractionCreate {
  tender_id: string;
  interaction_type: 'view' | 'save' | 'apply' | 'dismiss' | 'rate_positive' | 'rate_negative';
  time_spent_seconds?: number;
  feedback_reason?: string;
}

export interface InteractionStats {
  total_interactions: number;
  views_count: number;
  saves_count: number;
  applies_count: number;
  dismisses_count: number;
  positive_rates_count: number;
  negative_rates_count: number;
  avg_time_spent?: number;
  most_engaged_categories: string[];
  most_engaged_regions: string[];
}

export interface LearnedInsight {
  insight_type: string;
  message: string;
  suggested_value: string | string[] | Record<string, any>;
  confidence: number;                  // 0-1
  interaction_count: number;
}

export interface ProfileRecommendations {
  insights: LearnedInsight[];
  completion_tips: string[];
  estimated_improvement?: string;
}

export interface WizardStep {
  step: number;
  data: Partial<CompanyProfileCreateStep1 & CompanyProfileCreateStep2>;
}

// Updated to 2-step wizard (down from 4)
export const WIZARD_STEPS = [
  {
    id: 1,
    title: "Tell us about your business",
    description: "Essential information for finding relevant tenders",
    fields: [
      "primary_sector",
      "active_sectors",
      "sub_sectors",
      "preferred_regions",
      "keywords"
    ]
  },
  {
    id: 2,
    title: "Refine your preferences",
    description: "Optional details to improve recommendation quality",
    fields: [
      "company_size",
      "years_in_operation",
      "certifications",
      "budget_min",
      "budget_max"
    ]
  }
] as const;

// Validation constants
export const VALIDATION = {
  ACTIVE_SECTORS: { MIN: 1, MAX: 5 },
  KEYWORDS: { MIN: 3, MAX: 10 },
  REGIONS: { MIN: 1, MAX: 5 }
} as const;

// Company size options
export const COMPANY_SIZES = [
  { value: 'startup', label: 'Startup (<10 employees)' },
  { value: 'small', label: 'Small (10-50 employees)' },
  { value: 'medium', label: 'Medium (50-200 employees)' },
  { value: 'large', label: 'Large (200+ employees)' }
] as const;

// Years in operation options
export const YEARS_OPTIONS = [
  { value: '<1', label: 'Less than 1 year' },
  { value: '1-3', label: '1-3 years' },
  { value: '3-5', label: '3-5 years' },
  { value: '5-10', label: '5-10 years' },
  { value: '10+', label: '10+ years' }
] as const;
