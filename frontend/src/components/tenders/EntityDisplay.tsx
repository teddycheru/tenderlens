'use client';

import { ExtractedEntities } from '@/types/ai';
import {
  Calendar,
  DollarSign,
  CheckCircle,
  Award,
  Building,
  MapPin,
  Mail,
  Phone
} from 'lucide-react';

interface EntityDisplayProps {
  entities?: ExtractedEntities;
}

export function EntityDisplay({ entities }: EntityDisplayProps) {
  if (!entities) {
    return null;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Extracted Information</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Deadline */}
        {entities.deadline && (
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Deadline</span>
            </div>
            <p className="font-medium text-gray-900 dark:text-gray-100">{entities.deadline}</p>
          </div>
        )}

        {/* Budget */}
        {entities.budget && (
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="h-4 w-4 text-green-600 dark:text-green-400" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Budget</span>
            </div>
            <p className="font-medium text-gray-900 dark:text-gray-100">{entities.budget}</p>
          </div>
        )}
      </div>

      {/* Requirements */}
      {entities.requirements && entities.requirements.length > 0 && (
        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Key Requirements</span>
          </div>
          <ul className="space-y-2">
            {entities.requirements.map((req, idx) => (
              <li key={idx} className="text-sm flex gap-2 text-gray-700 dark:text-gray-300">
                <span className="text-purple-600 dark:text-purple-400">•</span>
                <span>{req}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Qualifications */}
      {entities.qualifications && entities.qualifications.length > 0 && (
        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-3">
            <Award className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Qualifications</span>
          </div>
          <ul className="space-y-2">
            {entities.qualifications.map((qual, idx) => (
              <li key={idx} className="text-sm flex gap-2 text-gray-700 dark:text-gray-300">
                <span className="text-yellow-600 dark:text-yellow-400">•</span>
                <span>{qual}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Organizations & Locations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {entities.organizations && entities.organizations.length > 0 && (
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-3">
              <Building className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Organizations</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {entities.organizations.map((org, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 rounded text-xs"
                >
                  {org}
                </span>
              ))}
            </div>
          </div>
        )}

        {entities.locations && entities.locations.length > 0 && (
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="h-4 w-4 text-red-600 dark:text-red-400" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Locations</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {entities.locations.map((loc, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded text-xs"
                >
                  {loc}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Contact Info */}
      {entities.contact_info && (
        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Contact Information</span>
          </div>
          <div className="space-y-2">
            {entities.contact_info.email && (
              <div className="flex items-center gap-2 text-sm">
                <Mail className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <a
                  href={`mailto:${entities.contact_info.email}`}
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  {entities.contact_info.email}
                </a>
              </div>
            )}
            {entities.contact_info.phone && (
              <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                <Phone className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <span>{entities.contact_info.phone}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
