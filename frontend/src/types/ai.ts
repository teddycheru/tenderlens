/**
 * AI-related TypeScript types for TenderLens.
 * Corresponds to backend AI schemas.
 */

export interface ExtractedEntities {
  deadline?: string;
  budget?: string;
  requirements?: string[];
  qualifications?: string[];
  organizations?: string[];
  locations?: string[];
  contact_info?: {
    email?: string;
    phone?: string;
  };
}

export interface AIProcessRequest {
  tender_id: string;
  force_reprocess?: boolean;
  doc_url?: string;
}

export interface AIProcessResponse {
  tender_id: string;
  summary?: string;
  entities?: ExtractedEntities;
  quick_scan?: string;
  task_id?: string;
  cached?: boolean;
  processing_time_ms?: number;
}

export interface QuickScanRequest {
  title: string;
  description: string;
}

export interface QuickScanResponse {
  quick_scan: string;
}

export interface AIStatusResponse {
  tender_id: string;
  ai_processed: boolean;
  ai_processed_at?: string;
  has_summary: boolean;
  has_entities: boolean;
  word_count?: number;
}

export interface BatchProcessRequest {
  tender_ids: string[];
}

export interface BatchProcessResponse {
  total: number;
  task_ids: string[];
  status: string;
}

export interface AIHealthResponse {
  ai_enabled: boolean;
  summarizer_available: boolean;
  summarizer_provider?: string;
  entity_extractor_available: boolean;
  cache_available: boolean;
}
