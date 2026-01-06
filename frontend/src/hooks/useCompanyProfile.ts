import { useState, useEffect, useCallback } from 'react'
import { companyProfileApi } from '@/lib/company-profile'
import type {
  CompanyTenderProfile,
  CompanyProfileCreateStep1,
  CompanyProfileCreateStep2,
  CompanyProfileUpdate,
  ProfileOptions
} from '@/types/profile'

/**
 * Hook to fetch and manage the current user's company profile
 */
export function useCompanyProfile() {
  const [profile, setProfile] = useState<CompanyTenderProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchProfile = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await companyProfileApi.getMyProfile()
      setProfile(data)
    } catch (err: any) {
      console.error('Error fetching company profile:', err)
      // Don't set error if profile doesn't exist (404) - this is expected for new users
      if (err.response?.status !== 404) {
        setError(err.response?.data?.detail || 'Failed to fetch company profile')
      }
      setProfile(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

  return { profile, loading, error, refetch: fetchProfile }
}

/**
 * Hook to manage profile creation and updates
 */
export function useProfileMutation() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const createProfileStep1 = async (data: CompanyProfileCreateStep1) => {
    try {
      setLoading(true)
      setError(null)
      const profile = await companyProfileApi.createProfileStep1(data)
      return profile
    } catch (err: any) {
      console.error('Error creating profile (step 1):', err)
      const errorMessage = err.response?.data?.detail || 'Failed to create profile'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const completeProfileStep2 = async (data: CompanyProfileCreateStep2) => {
    try {
      setLoading(true)
      setError(null)
      const profile = await companyProfileApi.completeProfileStep2(data)
      return profile
    } catch (err: any) {
      console.error('Error completing profile (step 2):', err)
      const errorMessage = err.response?.data?.detail || 'Failed to complete profile'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (updates: CompanyProfileUpdate) => {
    try {
      setLoading(true)
      setError(null)
      const profile = await companyProfileApi.updateProfile(updates)
      return profile
    } catch (err: any) {
      console.error('Error updating profile:', err)
      const errorMessage = err.response?.data?.detail || 'Failed to update profile'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const deleteProfile = async () => {
    try {
      setLoading(true)
      setError(null)
      await companyProfileApi.deleteProfile()
    } catch (err: any) {
      console.error('Error deleting profile:', err)
      const errorMessage = err.response?.data?.detail || 'Failed to delete profile'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return {
    createProfileStep1,
    completeProfileStep2,
    updateProfile,
    deleteProfile,
    loading,
    error
  }
}

/**
 * Hook to fetch profile options (sectors, regions, certifications, etc.)
 */
export function useProfileOptions() {
  const [options, setOptions] = useState<ProfileOptions | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await companyProfileApi.getProfileOptions()
        setOptions(data)
      } catch (err: any) {
        console.error('Error fetching profile options:', err)
        setError(err.response?.data?.detail || 'Failed to fetch profile options')
      } finally {
        setLoading(false)
      }
    }

    fetchOptions()
  }, [])

  return { options, loading, error }
}

/**
 * Hook to fetch profile statistics
 */
export function useProfileStats() {
  const [stats, setStats] = useState<{
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
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await companyProfileApi.getProfileStats()
      setStats(data)
    } catch (err: any) {
      console.error('Error fetching profile stats:', err)
      setError(err.response?.data?.detail || 'Failed to fetch profile stats')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  return { stats, loading, error, refetch: fetchStats }
}

/**
 * Hook to get keyword suggestions for a sector
 */
export function useKeywordSuggestions(sector: string | null) {
  const [keywords, setKeywords] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sector) {
      setKeywords([])
      return
    }

    const fetchKeywords = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await companyProfileApi.getKeywordSuggestions(sector)
        setKeywords(data)
      } catch (err: any) {
        console.error('Error fetching keyword suggestions:', err)
        setError(err.response?.data?.detail || 'Failed to fetch keyword suggestions')
        setKeywords([])
      } finally {
        setLoading(false)
      }
    }

    fetchKeywords()
  }, [sector])

  return { keywords, loading, error }
}

/**
 * Hook for onboarding state management
 */
export function useOnboardingState() {
  const [currentStep, setCurrentStep] = useState(1)
  const [profileId, setProfileId] = useState<string | null>(null)
  const [isComplete, setIsComplete] = useState(false)

  const handleStep1Complete = (id: string) => {
    setProfileId(id)
    setCurrentStep(2)
  }

  const handleStep2Complete = () => {
    setIsComplete(true)
  }

  const handleSkipStep2 = () => {
    setIsComplete(true)
  }

  const reset = () => {
    setCurrentStep(1)
    setProfileId(null)
    setIsComplete(false)
  }

  return {
    currentStep,
    profileId,
    isComplete,
    handleStep1Complete,
    handleStep2Complete,
    handleSkipStep2,
    reset
  }
}
