'use client'

import { Mail, Phone, ExternalLink } from 'lucide-react'
import type { ContactData } from '@/types/tender'

interface ContactInfoProps {
  contact?: ContactData
}

export function ContactInfo({ contact }: ContactInfoProps) {
  if (!contact || ((!contact.emails || contact.emails.length === 0) && (!contact.phones || contact.phones.length === 0))) {
    return null
  }

  return (
    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <div className="p-2 bg-blue-100 dark:bg-blue-900/40 rounded-lg">
          <Mail size={24} className="text-blue-600 dark:text-blue-400" />
        </div>
        Contact Information
      </h3>

      <div className="space-y-4">
        {contact.emails && contact.emails.length > 0 && (
          <div>
            <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <Mail size={16} className="text-blue-600 dark:text-blue-400" />
              Email Address{contact.emails.length > 1 ? 'es' : ''}
            </p>
            <div className="space-y-2">
              {contact.emails.map((email, idx) => (
                <a
                  key={idx}
                  href={`mailto:${email}`}
                  className="block p-3 bg-white dark:bg-gray-800 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-blue-600 dark:text-blue-400 group-hover:underline break-all">
                      {email}
                    </span>
                    <ExternalLink size={14} className="text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 flex-shrink-0" />
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {contact.phones && contact.phones.length > 0 && (
          <div>
            <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <Phone size={16} className="text-blue-600 dark:text-blue-400" />
              Phone Number{contact.phones.length > 1 ? 's' : ''}
            </p>
            <div className="space-y-2">
              {contact.phones.map((phone, idx) => (
                <a
                  key={idx}
                  href={`tel:${phone}`}
                  className="block p-3 bg-white dark:bg-gray-800 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-blue-600 dark:text-blue-400 group-hover:underline">
                      {phone}
                    </span>
                    <ExternalLink size={14} className="text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 flex-shrink-0" />
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
