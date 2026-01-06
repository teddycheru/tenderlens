import api from './api'
import type {
  CompanyTenderProfile,
  CompanyProfileCreateStep1,
  CompanyProfileCreateStep2,
  CompanyProfileUpdate,
  ProfileOptions,
  CompanyProfileSummary
} from '@/types/profile'

export const companyProfileApi = {
  /**
   * Create profile with Step 1 data (critical fields)
   */
  async createProfileStep1(data: CompanyProfileCreateStep1): Promise<CompanyTenderProfile> {
    const response = await api.post('/company-profile/step1', data)
    return response.data
  },

  /**
   * Complete profile with Step 2 data (optional refinement)
   */
  async completeProfileStep2(data: CompanyProfileCreateStep2): Promise<CompanyTenderProfile> {
    const response = await api.put('/company-profile/step2', data)
    return response.data
  },

  /**
   * Get current user's company profile
   */
  async getMyProfile(): Promise<CompanyTenderProfile> {
    const response = await api.get('/company-profile')
    return response.data
  },

  /**
   * Get profile by company ID
   */
  async getProfileByCompanyId(companyId: string): Promise<CompanyTenderProfile> {
    const response = await api.get(`/company-profile/company/${companyId}`)
    return response.data
  },

  /**
   * Update company profile (partial update)
   */
  async updateProfile(updates: CompanyProfileUpdate): Promise<CompanyTenderProfile> {
    const response = await api.put('/company-profile', updates)
    return response.data
  },

  /**
   * Delete company profile
   */
  async deleteProfile(): Promise<void> {
    await api.delete('/company-profile')
  },

  /**
   * Get available profile options (sectors, regions, certifications, etc.)
   */
  async getProfileOptions(): Promise<ProfileOptions> {
    const response = await api.get('/company-profile/options')
    return response.data
  },

  /**
   * Get keyword suggestions for a specific sector
   */
  async getKeywordSuggestions(sector: string): Promise<string[]> {
    const response = await api.get(`/company-profile/options/keywords/${sector}`)
    return response.data
  },

  /**
   * Get profile statistics
   */
  async getProfileStats(): Promise<{
    completion_percentage: number
    is_tier1_complete: boolean
    is_tier2_complete: boolean
    profile_completed: boolean
    onboarding_step: number
    interaction_count: number
    active_sectors_count: number
    sub_sectors_count: number
    keywords_count: number
    certifications_count: number
    has_budget_range: boolean
    days_since_creation: number
  }> {
    const response = await api.get('/company-profile/stats')
    return response.data
  },

  // Admin endpoints
  async getIncompleteProfiles(limit: number = 100): Promise<CompanyProfileSummary[]> {
    const response = await api.get('/company-profile/admin/incomplete', { params: { limit } })
    return response.data
  },

  async getProfilesBySector(sector: string, limit: number = 100): Promise<CompanyProfileSummary[]> {
    const response = await api.get(`/company-profile/admin/sector/${sector}`, { params: { limit } })
    return response.data
  }
}
