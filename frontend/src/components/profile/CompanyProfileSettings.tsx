/**
 * Company Profile Settings Component
 * Allows users to view and edit their company tender profile
 */

'use client'

import React, { useState, useEffect } from 'react'
import { Building, Save, Trash2, TrendingUp, AlertCircle } from 'lucide-react'
import { useCompanyProfile, useProfileMutation, useProfileStats } from '@/hooks/useCompanyProfile'
import { useProfileOptions } from '@/hooks/useCompanyProfile'
import { CompanyProfileUpdate, VALIDATION } from '@/types/profile'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { useRouter } from 'next/navigation'

export function CompanyProfileSettings() {
  const router = useRouter()
  const { profile, loading: profileLoading, refetch } = useCompanyProfile()
  const { stats, loading: statsLoading } = useProfileStats()
  const { options } = useProfileOptions()
  const { updateProfile, deleteProfile, loading: mutating } = useProfileMutation()

  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState<CompanyProfileUpdate>({})

  // Initialize form data when profile loads
  useEffect(() => {
    if (profile && !isEditing) {
      setFormData({
        primary_sector: profile.primary_sector,
        active_sectors: profile.active_sectors,
        sub_sectors: profile.sub_sectors,
        preferred_regions: profile.preferred_regions,
        keywords: profile.keywords,
        company_size: profile.company_size,
        years_in_operation: profile.years_in_operation,
        certifications: profile.certifications || [],
        budget_min: profile.budget_min,
        budget_max: profile.budget_max,
      })
    }
  }, [profile, isEditing])

  const handleSave = async () => {
    try {
      await updateProfile(formData)
      toast.success('Company profile updated successfully!')
      setIsEditing(false)
      refetch()
    } catch (error) {
      // Error is already handled in the hook
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete your company profile? This action cannot be undone.')) {
      return
    }

    try {
      await deleteProfile()
      toast.success('Company profile deleted')
      refetch()
    } catch (error) {
      // Error is already handled in the hook
    }
  }

  const handleToggleActiveSector = (sector: string) => {
    const current = formData.active_sectors || []
    const updated = current.includes(sector)
      ? current.filter(s => s !== sector)
      : current.length < VALIDATION.ACTIVE_SECTORS.MAX
        ? [...current, sector]
        : current
    setFormData({ ...formData, active_sectors: updated })
  }

  const handleToggleRegion = (region: string) => {
    const current = formData.preferred_regions || []
    const updated = current.includes(region)
      ? current.filter(r => r !== region)
      : current.length < VALIDATION.REGIONS.MAX
        ? [...current, region]
        : current
    setFormData({ ...formData, preferred_regions: updated })
  }

  if (profileLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <Building className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No Company Profile
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          You haven&apos;t set up your company profile yet.
        </p>
        <button
          onClick={() => router.push('/onboarding')}
          className="inline-flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Building className="w-4 h-4" />
          Set Up Company Profile
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">
            Company Tender Profile
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Manage your company information and tender preferences
          </p>
        </div>
        {!isEditing ? (
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            Edit Profile
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={() => {
                setIsEditing(false)
                setFormData({
                  primary_sector: profile.primary_sector,
                  active_sectors: profile.active_sectors,
                  sub_sectors: profile.sub_sectors,
                  preferred_regions: profile.preferred_regions,
                  keywords: profile.keywords,
                  company_size: profile.company_size,
                  years_in_operation: profile.years_in_operation,
                  certifications: profile.certifications || [],
                  budget_min: profile.budget_min,
                  budget_max: profile.budget_max,
                })
              }}
              disabled={mutating}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={mutating}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {mutating ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        )}
      </div>

      {/* Completion Stats */}
      {stats && !statsLoading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900 dark:text-blue-300">
                Profile Completion
              </span>
            </div>
            <p className="text-2xl font-bold text-blue-600">{stats.completion_percentage}%</p>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Building className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-900 dark:text-green-300">
                Active Sectors
              </span>
            </div>
            <p className="text-2xl font-bold text-green-600">{stats.active_sectors_count}</p>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <AlertCircle className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-900 dark:text-purple-300">
                Interactions
              </span>
            </div>
            <p className="text-2xl font-bold text-purple-600">{stats.interaction_count}</p>
          </div>
        </div>
      )}

      {/* Profile Fields */}
      <div className="space-y-6 bg-gray-50 dark:bg-gray-700/50 rounded-lg p-6">
        {/* Primary Sector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Primary Sector (Identity)
          </label>
          {isEditing ? (
            <select
              value={formData.primary_sector || ''}
              onChange={(e) => setFormData({ ...formData, primary_sector: e.target.value })}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="">Select sector...</option>
              {options?.sectors.map(sector => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
            </select>
          ) : (
            <p className="text-gray-900 dark:text-white font-medium">{profile.primary_sector}</p>
          )}
        </div>

        {/* Active Sectors */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Active Work Sectors ({isEditing ? formData.active_sectors?.length || 0 : profile.active_sectors.length}/{VALIDATION.ACTIVE_SECTORS.MAX})
          </label>
          {isEditing ? (
            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto p-2 border rounded-lg dark:border-gray-600">
              {options?.sectors.map(sector => (
                <label
                  key={sector}
                  className={cn(
                    'flex items-center gap-2 p-2 rounded cursor-pointer',
                    formData.active_sectors?.includes(sector) ? 'bg-green-100 dark:bg-green-900/30' : 'hover:bg-gray-100 dark:hover:bg-gray-600'
                  )}
                >
                  <input
                    type="checkbox"
                    checked={formData.active_sectors?.includes(sector)}
                    onChange={() => handleToggleActiveSector(sector)}
                    disabled={
                      (formData.active_sectors?.length || 0) >= VALIDATION.ACTIVE_SECTORS.MAX &&
                      !formData.active_sectors?.includes(sector)
                    }
                    className="rounded text-green-600"
                  />
                  <span className="text-sm">{sector}</span>
                </label>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {profile.active_sectors.map(sector => (
                <span key={sector} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm dark:bg-green-900/30 dark:text-green-300">
                  {sector}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Sub-Sectors */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Specializations
          </label>
          <div className="flex flex-wrap gap-2">
            {(isEditing ? formData.sub_sectors : profile.sub_sectors)?.map(sector => (
              <span key={sector} className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm dark:bg-indigo-900/30 dark:text-indigo-300">
                {sector}
              </span>
            )) || <p className="text-gray-500 text-sm">No specializations added</p>}
          </div>
        </div>

        {/* Preferred Regions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Preferred Regions ({isEditing ? formData.preferred_regions?.length || 0 : profile.preferred_regions.length}/{VALIDATION.REGIONS.MAX})
          </label>
          {isEditing ? (
            <div className="grid grid-cols-3 gap-2 p-2 border rounded-lg dark:border-gray-600">
              {options?.regions.map(region => (
                <label
                  key={region}
                  className={cn(
                    'flex items-center gap-2 p-2 rounded cursor-pointer',
                    formData.preferred_regions?.includes(region) ? 'bg-blue-100 dark:bg-blue-900/30' : 'hover:bg-gray-100 dark:hover:bg-gray-600'
                  )}
                >
                  <input
                    type="checkbox"
                    checked={formData.preferred_regions?.includes(region)}
                    onChange={() => handleToggleRegion(region)}
                    disabled={
                      (formData.preferred_regions?.length || 0) >= VALIDATION.REGIONS.MAX &&
                      !formData.preferred_regions?.includes(region)
                    }
                    className="rounded text-blue-600"
                  />
                  <span className="text-sm">{region}</span>
                </label>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {profile.preferred_regions.map(region => (
                <span key={region} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm dark:bg-blue-900/30 dark:text-blue-300">
                  {region}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Keywords */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Core Keywords ({isEditing ? formData.keywords?.length || 0 : profile.keywords.length})
          </label>
          <div className="flex flex-wrap gap-2">
            {(isEditing ? formData.keywords : profile.keywords)?.map(keyword => (
              <span key={keyword} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm dark:bg-blue-900/30 dark:text-blue-300 font-medium">
                {keyword}
              </span>
            ))}
          </div>
        </div>

        {/* Company Size & Years */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Company Size
            </label>
            <p className="text-gray-900 dark:text-white">
              {profile.company_size || 'Not specified'}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Years in Operation
            </label>
            <p className="text-gray-900 dark:text-white">
              {profile.years_in_operation || 'Not specified'}
            </p>
          </div>
        </div>

        {/* Budget Range */}
        {(profile.budget_min || profile.budget_max) && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Budget Range
            </label>
            <p className="text-gray-900 dark:text-white">
              {profile.budget_min?.toLocaleString()} - {profile.budget_max?.toLocaleString()} {profile.budget_currency}
            </p>
          </div>
        )}
      </div>

      {/* Danger Zone */}
      <div className="border-t border-red-200 dark:border-red-800 pt-6">
        <h3 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">
          Danger Zone
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Deleting your company profile will remove all tender preferences and interaction history.
        </p>
        <button
          onClick={handleDelete}
          disabled={mutating}
          className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
        >
          <Trash2 className="w-4 h-4" />
          Delete Company Profile
        </button>
      </div>
    </div>
  )
}
