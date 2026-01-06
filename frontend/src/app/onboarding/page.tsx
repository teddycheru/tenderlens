'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { ProfileSetupWizard } from '@/components/profile/ProfileSetupWizard'
import { useCompanyProfile } from '@/hooks/useCompanyProfile'
import { toast } from 'sonner'

export default function OnboardingPage() {
  const router = useRouter()
  const { profile, loading } = useCompanyProfile()

  // If user already has a complete profile, redirect to dashboard
  useEffect(() => {
    if (!loading && profile?.profile_completed) {
      toast.info('Your profile is already set up')
      router.push('/dashboard')
    }
  }, [profile, loading, router])

  const handleComplete = (profileId: string) => {
    toast.success('Profile created successfully! Welcome to TenderLens 🎉')
    router.push('/dashboard')
  }

  const handleSkip = () => {
    toast.info('You can complete your profile later from settings')
    router.push('/dashboard')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome to TenderLens!
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Let&apos;s set up your company profile to start receiving personalized tender recommendations
          </p>
        </div>

        {/* Wizard */}
        <ProfileSetupWizard
          onComplete={handleComplete}
          onSkip={handleSkip}
        />

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            Your data is secure and will only be used to improve your tender recommendations
          </p>
        </div>
      </div>
    </div>
  )
}
