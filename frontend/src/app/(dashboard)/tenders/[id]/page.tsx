'use client'

import { useParams, useRouter } from 'next/navigation'
import { formatDistanceToNow, format, isPast } from 'date-fns'
import { ArrowLeft, Calendar, MapPin, Tag, Building, Sparkles, RefreshCw, ExternalLink, Badge } from 'lucide-react'
import { useTender } from '@/hooks/useTenders'
import { aiApi } from '@/lib/ai'
import { EntityDisplay } from '@/components/tenders/EntityDisplay'
import { GeneratedContent } from '@/components/tenders/GeneratedContent'
import { FinancialInfo } from '@/components/tenders/FinancialInfo'
import { ContactInfo } from '@/components/tenders/ContactInfo'
import { DatesDisplay } from '@/components/tenders/DatesDisplay'
import { RequirementsAndSpecs } from '@/components/tenders/RequirementsAndSpecs'
import { OrganizationInfo } from '@/components/tenders/OrganizationInfo'
import { useState } from 'react'

export default function TenderDetailPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string
  const [aiProcessing, setAiProcessing] = useState(false)
  const [aiError, setAiError] = useState('')

  const { tender, loading, error, refetch } = useTender(id)

  const handleProcessAI = async () => {
    try {
      setAiProcessing(true)
      setAiError('')

      // Trigger AI processing
      await aiApi.processTender(id)

      // Wait a bit for processing to start, then refetch
      setTimeout(() => {
        refetch()
        setAiProcessing(false)
      }, 1000)
    } catch (err) {
      setAiError(err instanceof Error ? err.message : 'Failed to process tender with AI')
      setAiProcessing(false)
    }
  }

  const handleReprocessAI = async () => {
    try {
      setAiProcessing(true)
      setAiError('')

      // Force reprocessing
      await aiApi.processTender(id, true)

      // Wait and refetch
      setTimeout(() => {
        refetch()
        setAiProcessing(false)
      }, 1000)
    } catch (err) {
      setAiError(err instanceof Error ? err.message : 'Failed to reprocess tender')
      setAiProcessing(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading tender details...</p>
        </div>
      </div>
    )
  }

  if (error || !tender) {
    return (
      <div>
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft size={20} />
          Back to Tenders
        </button>
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 px-6 py-4 rounded-lg">
          {error || 'Tender not found'}
        </div>
      </div>
    )
  }

  const isExpired = tender.deadline && isPast(new Date(tender.deadline))
  const isClosingSoon = tender.deadline && !isPast(new Date(tender.deadline)) && Date.now() + 7 * 24 * 60 * 60 * 1000 > new Date(tender.deadline).getTime()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <button
          onClick={() => router.back()}
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors hover:underline"
        >
          <ArrowLeft size={20} />
          <span className="text-sm font-medium">Back to Tenders</span>
        </button>
        {tender.source_url && (
          <a
            href={tender.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
          >
            <ExternalLink size={16} />
            View Original
          </a>
        )}
      </div>

      {/* Title Section */}
      <div className="bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 rounded-lg p-8 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="flex items-start justify-between gap-4 mb-4">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white leading-tight flex-1">
            {tender.title}
          </h1>
          {tender.status && (
            <span className={`px-4 py-2 rounded-full text-sm font-semibold whitespace-nowrap ${
              tender.status === 'published'
                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}>
              {tender.status === 'published' ? 'Active' : 'Closed'}
            </span>
          )}
        </div>

        {/* Quick Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {tender.category && (
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <p className="text-xs font-medium text-blue-600 dark:text-blue-400 uppercase tracking-wide">Category</p>
              <p className="text-base font-semibold text-gray-900 dark:text-white mt-1">{tender.category}</p>
            </div>
          )}

          {tender.region && (
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <p className="text-xs font-medium text-green-600 dark:text-green-400 uppercase tracking-wide">Region</p>
              <p className="text-base font-semibold text-gray-900 dark:text-white mt-1">{tender.region}</p>
            </div>
          )}

          {tender.deadline && (
            <div className={`p-4 rounded-lg border ${
              isExpired
                ? 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700'
                : isClosingSoon
                  ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                  : 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800'
            }`}>
              <p className={`text-xs font-medium uppercase tracking-wide ${
                isExpired
                  ? 'text-gray-600 dark:text-gray-400'
                  : isClosingSoon
                    ? 'text-red-600 dark:text-red-400'
                    : 'text-orange-600 dark:text-orange-400'
              }`}>
                {isExpired ? 'Expired' : 'Deadline'}
              </p>
              <p className={`text-base font-semibold mt-1 ${
                isExpired
                  ? 'text-gray-900 dark:text-white line-through'
                  : isClosingSoon
                    ? 'text-red-700 dark:text-red-300'
                    : 'text-gray-900 dark:text-white'
              }`}>
                {formatDistanceToNow(new Date(tender.deadline), { addSuffix: true })}
              </p>
            </div>
          )}

          {tender.published_date && (
            <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
              <p className="text-xs font-medium text-purple-600 dark:text-purple-400 uppercase tracking-wide">Published</p>
              <p className="text-base font-semibold text-gray-900 dark:text-white mt-1">{format(new Date(tender.published_date), 'MMM dd')}</p>
            </div>
          )}
        </div>
      </div>

      {/* Generated Content Section */}
      {tender.clean_description || tender.highlights || tender.ai_summary ? (
        <GeneratedContent
          cleanDescription={tender.clean_description}
          highlights={tender.highlights}
          aiSummary={tender.ai_summary}
        />
      ) : null}

      {/* Key Information Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <DatesDisplay dates={tender.extracted_data?.dates} deadline={tender.deadline} />
          <ContactInfo contact={tender.extracted_data?.contact} />
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <FinancialInfo financial={tender.extracted_data?.financial} />
          <OrganizationInfo
            organization={tender.extracted_data?.organization}
            addresses={tender.extracted_data?.addresses}
          />
        </div>
      </div>

      {/* Requirements and Specifications */}
      <RequirementsAndSpecs extractedData={tender.extracted_data} />

      {/* Additional AI Details */}
      {!tender.clean_description && !tender.highlights && (
        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <Sparkles size={24} className="text-purple-600 dark:text-purple-400" />
              Additional Processing
            </h3>
            {tender.ai_processed && (
              <button
                onClick={handleReprocessAI}
                disabled={aiProcessing}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw size={16} className={aiProcessing ? 'animate-spin' : ''} />
                Refresh
              </button>
            )}
          </div>

          {aiError && (
            <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 rounded-lg text-sm">
              {aiError}
            </div>
          )}

          {!tender.ai_processed && !aiProcessing && (
            <button
              onClick={handleProcessAI}
              className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
            >
              <Sparkles size={20} />
              Extract Additional Details
            </button>
          )}

          {aiProcessing && (
            <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-purple-500 border-t-transparent"></div>
                <p className="text-gray-900 dark:text-white font-medium">Processing tender...</p>
              </div>
            </div>
          )}

          {tender.ai_processed && tender.extracted_entities && (
            <div className="space-y-6">
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Extracted Information</h4>
                <EntityDisplay entities={tender.extracted_entities} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer with Metadata */}
      <div className="pt-8 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-400">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {tender.created_at && (
            <div>
              <p className="font-medium text-gray-900 dark:text-white">Added to Platform</p>
              <p>{format(new Date(tender.created_at), 'PPP')}</p>
            </div>
          )}
          {tender.content_generated_at && (
            <div>
              <p className="font-medium text-gray-900 dark:text-white">Content Generated</p>
              <p>{format(new Date(tender.content_generated_at), 'PPP')}</p>
            </div>
          )}
          {tender.source && (
            <div>
              <p className="font-medium text-gray-900 dark:text-white">Source</p>
              <p className="capitalize">{tender.source}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
