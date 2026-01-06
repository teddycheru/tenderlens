'use client'

import { Building2, MapPin } from 'lucide-react'
import type { OrganizationData, AddressesData } from '@/types/tender'

interface OrganizationInfoProps {
  organization?: OrganizationData
  addresses?: AddressesData
}

export function OrganizationInfo({ organization, addresses }: OrganizationInfoProps) {
  if (!organization && !addresses) return null

  const hasData = organization?.name || (addresses?.regions && addresses.regions.length > 0)

  if (!hasData) return null

  return (
    <div className="bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-900/20 dark:to-blue-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-indigo-100 dark:bg-indigo-900/40 rounded-lg">
          <Building2 size={24} className="text-indigo-600 dark:text-indigo-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Organization</h3>
      </div>

      <div className="space-y-4">
        {organization?.name && (
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium mb-2">Organization Name</p>
            <p className="text-base font-semibold text-gray-900 dark:text-white">{organization.name}</p>
            {organization.type && (
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">Type: {organization.type}</p>
            )}
          </div>
        )}

        {addresses?.regions && addresses.regions.length > 0 && (
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium mb-2 flex items-center gap-2">
              <MapPin size={16} className="text-indigo-600 dark:text-indigo-400" />
              Location{addresses.regions.length > 1 ? 's' : ''}
            </p>
            <div className="space-y-1">
              {addresses.regions.map((region, idx) => (
                <p key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                  {region}
                </p>
              ))}
            </div>
          </div>
        )}

        {addresses?.po_boxes && addresses.po_boxes.length > 0 && (
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium mb-2">P.O. Box{addresses.po_boxes.length > 1 ? 'es' : ''}</p>
            <div className="space-y-1">
              {addresses.po_boxes.map((poBox, idx) => (
                <p key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                  {poBox}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
