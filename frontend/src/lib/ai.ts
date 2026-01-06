/**
 * AI API client for TenderLens frontend.
 */

import api from './api'
import {
  AIProcessRequest,
  AIProcessResponse,
  QuickScanRequest,
  QuickScanResponse,
  AIStatusResponse,
  BatchProcessRequest,
  BatchProcessResponse,
  AIHealthResponse
} from '@/types/ai'

export const aiApi = {
  /**
   * Process a tender with AI (summarization + entity extraction).
   * @param tenderId - Tender UUID
   * @param forceReprocess - Force reprocessing even if cached
   * @param docUrl - Optional document URL to process
   */
  processTender: async (
    tenderId: string,
    forceReprocess: boolean = false,
    docUrl?: string
  ): Promise<AIProcessResponse> => {
    const response = await api.post<AIProcessResponse>('/ai/process', {
      tender_id: tenderId,
      force_reprocess: forceReprocess,
      doc_url: docUrl,
    })
    return response.data
  },

  /**
   * Get AI processing status for a tender.
   * @param tenderId - Tender UUID
   */
  getAIStatus: async (tenderId: string): Promise<AIStatusResponse> => {
    const response = await api.get<AIStatusResponse>(`/ai/status/${tenderId}`)
    return response.data
  },

  /**
   * Get AI processing results for a tender.
   * @param tenderId - Tender UUID
   */
  getAIResults: async (tenderId: string): Promise<AIProcessResponse> => {
    const response = await api.get<AIProcessResponse>(`/ai/result/${tenderId}`)
    return response.data
  },

  /**
   * Generate quick scan for a tender.
   * @param title - Tender title
   * @param description - Tender description
   */
  generateQuickScan: async (
    title: string,
    description: string
  ): Promise<QuickScanResponse> => {
    const response = await api.post<QuickScanResponse>('/ai/quick-scan', {
      title,
      description,
    })
    return response.data
  },

  /**
   * Batch process multiple tenders.
   * @param tenderIds - Array of tender UUIDs
   */
  batchProcess: async (tenderIds: string[]): Promise<BatchProcessResponse> => {
    const response = await api.post<BatchProcessResponse>('/ai/batch-process', {
      tender_ids: tenderIds,
    })
    return response.data
  },

  /**
   * Invalidate cached AI results for a tender.
   * @param tenderId - Tender UUID
   */
  invalidateCache: async (tenderId: string): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/ai/cache/${tenderId}`)
    return response.data
  },

  /**
   * Check AI service health status.
   */
  checkHealth: async (): Promise<AIHealthResponse> => {
    const response = await api.get<AIHealthResponse>('/ai/health')
    return response.data
  },
}
