import { ExtractedEntities } from './ai'

export interface FinancialData {
  bid_security_amount?: number
  bid_security_currency?: string
  document_fee?: number
  fee_currency?: string
  other_amounts?: number[]
}

export interface ContactData {
  emails: string[]
  phones: string[]
}

export interface DatesData {
  closing_date?: string
  published_date?: string
  closing_date_original?: string
}

export interface SpecificationItem {
  [key: string]: string
}

export interface OrganizationData {
  name: string
  type?: string
}

export interface AddressesData {
  po_boxes: string[]
  regions: string[]
}

export interface ExtractedData {
  financial?: FinancialData
  contact?: ContactData
  dates?: DatesData
  requirements?: string[]
  specifications?: SpecificationItem[]
  organization?: OrganizationData
  addresses?: AddressesData
  language_flag?: string
  tender_type?: string
  is_award_notification?: boolean
}

export interface Tender {
  id: string
  title: string
  description: string
  deadline?: string
  budget?: number
  category?: string
  region?: string
  source_url?: string
  source?: string
  organization?: string
  requirements?: string
  is_active?: boolean
  created_at: string
  updated_at: string
  published_date?: string
  status?: string

  // Generated Content Fields (Content Generator)
  clean_description?: string
  highlights?: string
  extracted_data?: ExtractedData
  content_generated_at?: string
  content_generation_errors?: any[]

  // AI Processing Fields (Phase 2)
  ai_summary?: string
  ai_processed?: boolean
  ai_processed_at?: string
  extracted_entities?: ExtractedEntities
  raw_text?: string
  word_count?: number
}

export interface TenderFilters {
  search?: string
  category?: string
  region?: string
  min_budget?: number
  max_budget?: number
  is_active?: boolean
  skip?: number
  limit?: number
}

export interface TenderListResponse {
  items: Tender[]
  total: number
  page: number
  size: number
  pages: number
}
