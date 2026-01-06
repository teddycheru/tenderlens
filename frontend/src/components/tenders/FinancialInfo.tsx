'use client'

import { DollarSign } from 'lucide-react'
import type { FinancialData } from '@/types/tender'

interface FinancialInfoProps {
  financial?: FinancialData
}

export function FinancialInfo({ financial }: FinancialInfoProps) {
  if (!financial) return null

  const hasData =
    financial.bid_security_amount ||
    financial.document_fee ||
    (financial.other_amounts && financial.other_amounts.length > 0)

  if (!hasData) return null

  const formatCurrency = (amount?: number, currency?: string) => {
    if (!amount) return null
    return `${currency || 'ETB'} ${amount.toLocaleString()}`
  }

  return (
    <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-green-100 dark:bg-green-900/40 rounded-lg">
          <DollarSign size={24} className="text-green-600 dark:text-green-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Financial Information</h3>
      </div>

      <div className="space-y-3">
        {financial.bid_security_amount && (
          <div className="flex justify-between items-start p-3 bg-white dark:bg-gray-800 rounded-lg">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Bid Security</p>
              <p className="text-xs text-gray-500 dark:text-gray-500">Required guarantee amount</p>
            </div>
            <p className="text-base font-bold text-green-600 dark:text-green-400 text-right">
              {formatCurrency(financial.bid_security_amount, financial.bid_security_currency)}
            </p>
          </div>
        )}

        {financial.document_fee && (
          <div className="flex justify-between items-start p-3 bg-white dark:bg-gray-800 rounded-lg">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Document Fee</p>
              <p className="text-xs text-gray-500 dark:text-gray-500">Cost to obtain tender documents</p>
            </div>
            <p className="text-base font-bold text-green-600 dark:text-green-400 text-right">
              {formatCurrency(financial.document_fee, financial.fee_currency)}
            </p>
          </div>
        )}

        {financial.other_amounts && financial.other_amounts.length > 0 && (
          <div className="flex justify-between items-start p-3 bg-white dark:bg-gray-800 rounded-lg">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Additional Fees</p>
              <p className="text-xs text-gray-500 dark:text-gray-500">{financial.other_amounts.length} other amount(s)</p>
            </div>
            <div className="text-right">
              {financial.other_amounts.map((amount, idx) => (
                <p key={idx} className="text-sm text-green-600 dark:text-green-400">
                  {formatCurrency(amount)}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
