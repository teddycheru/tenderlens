/**
 * FeedbackButtons Component
 * User interaction buttons for tender recommendations
 */

import React, { useState } from 'react';
import { useTenderActions } from '@/hooks/useRecommendations';

interface FeedbackButtonsProps {
  tenderId: string;
  layout?: 'horizontal' | 'vertical';
  size?: 'sm' | 'md' | 'lg';
  showLabels?: boolean;
  onSave?: () => void;
  onDismiss?: () => void;
  onApply?: () => void;
  className?: string;
}

export default function FeedbackButtons({
  tenderId,
  layout = 'horizontal',
  size = 'md',
  showLabels = true,
  onSave,
  onDismiss,
  onApply,
  className = '',
}: FeedbackButtonsProps) {
  const {
    saveTender,
    unsaveTender,
    dismissTender,
    markAsApplied,
    isSaved,
    isDismissed,
  } = useTenderActions();

  const [loading, setLoading] = useState<{
    save?: boolean;
    dismiss?: boolean;
    apply?: boolean;
  }>({});
  const [showDismissReason, setShowDismissReason] = useState(false);

  const saved = isSaved(tenderId);
  const dismissed = isDismissed(tenderId);

  const handleSave = async () => {
    setLoading({ ...loading, save: true });
    try {
      if (saved) {
        unsaveTender(tenderId);
      } else {
        await saveTender(tenderId);
      }
      onSave?.();
    } catch (error) {
      console.error('Failed to save tender:', error);
    } finally {
      setLoading({ ...loading, save: false });
    }
  };

  const handleDismiss = async (reason?: string) => {
    setLoading({ ...loading, dismiss: true });
    try {
      await dismissTender(tenderId, reason);
      setShowDismissReason(false);
      onDismiss?.();
    } catch (error) {
      console.error('Failed to dismiss tender:', error);
    } finally {
      setLoading({ ...loading, dismiss: false });
    }
  };

  const handleApply = async () => {
    setLoading({ ...loading, apply: true });
    try {
      await markAsApplied(tenderId);
      onApply?.();
    } catch (error) {
      console.error('Failed to track application:', error);
    } finally {
      setLoading({ ...loading, apply: false });
    }
  };

  const sizeClasses = {
    sm: 'px-2.5 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  const buttonClass = `${sizeClasses[size]} font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed`;

  if (dismissed) {
    return (
      <div className={`text-sm text-gray-500 italic ${className}`}>
        Dismissed
      </div>
    );
  }

  return (
    <div className={className}>
      <div
        className={`flex ${
          layout === 'horizontal' ? 'flex-row gap-3' : 'flex-col gap-2'
        }`}
      >
        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={loading.save}
          className={`${buttonClass} ${
            saved
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          <div className="flex items-center justify-center gap-2">
            {loading.save ? (
              <Spinner />
            ) : (
              <svg
                className="w-4 h-4"
                fill={saved ? 'currentColor' : 'none'}
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
                />
              </svg>
            )}
            {showLabels && <span>{saved ? 'Saved' : 'Save'}</span>}
          </div>
        </button>

        {/* Dismiss Button */}
        <button
          onClick={() => setShowDismissReason(true)}
          disabled={loading.dismiss}
          className={`${buttonClass} bg-white text-gray-700 border border-gray-300 hover:bg-gray-50`}
        >
          <div className="flex items-center justify-center gap-2">
            {loading.dismiss ? (
              <Spinner />
            ) : (
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            )}
            {showLabels && <span>Dismiss</span>}
          </div>
        </button>

        {/* Apply Button */}
        <button
          onClick={handleApply}
          disabled={loading.apply}
          className={`${buttonClass} bg-green-600 text-white hover:bg-green-700`}
        >
          <div className="flex items-center justify-center gap-2">
            {loading.apply ? (
              <Spinner />
            ) : (
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            )}
            {showLabels && <span>Apply</span>}
          </div>
        </button>
      </div>

      {/* Dismiss Reason Modal */}
      {showDismissReason && (
        <DismissReasonModal
          onConfirm={handleDismiss}
          onCancel={() => setShowDismissReason(false)}
        />
      )}
    </div>
  );
}

/**
 * Dismiss reason modal component
 */
function DismissReasonModal({
  onConfirm,
  onCancel,
}: {
  onConfirm: (reason?: string) => void;
  onCancel: () => void;
}) {
  const [reason, setReason] = useState('');
  const [selectedReason, setSelectedReason] = useState<string>('');

  const commonReasons = [
    'Not relevant to my company',
    'Budget too high',
    'Wrong location',
    'Deadline too soon',
    'Already applied',
    'Other',
  ];

  const handleSubmit = () => {
    const finalReason = selectedReason === 'Other' ? reason : selectedReason;
    onConfirm(finalReason || undefined);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Why are you dismissing this tender?
          </h3>

          <div className="space-y-2 mb-4">
            {commonReasons.map((r) => (
              <label key={r} className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                <input
                  type="radio"
                  name="dismissReason"
                  value={r}
                  checked={selectedReason === r}
                  onChange={(e) => setSelectedReason(e.target.value)}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="text-sm text-gray-700">{r}</span>
              </label>
            ))}
          </div>

          {selectedReason === 'Other' && (
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Please specify your reason..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={3}
            />
          )}

          <div className="flex gap-3 mt-6">
            <button
              onClick={onCancel}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!selectedReason}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Quick action buttons (icon only, compact)
 */
export function QuickActionButtons({
  tenderId,
  onSave,
  onDismiss,
  className = '',
}: {
  tenderId: string;
  onSave?: () => void;
  onDismiss?: () => void;
  className?: string;
}) {
  const { saveTender, unsaveTender, dismissTender, isSaved } = useTenderActions();
  const [loading, setLoading] = useState(false);
  const saved = isSaved(tenderId);

  const handleSave = async () => {
    setLoading(true);
    try {
      if (saved) {
        unsaveTender(tenderId);
      } else {
        await saveTender(tenderId);
      }
      onSave?.();
    } catch (error) {
      console.error('Failed to save tender:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDismiss = async () => {
    setLoading(true);
    try {
      await dismissTender(tenderId);
      onDismiss?.();
    } catch (error) {
      console.error('Failed to dismiss tender:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <button
        onClick={handleSave}
        disabled={loading}
        className={`p-2 rounded-lg transition-colors ${
          saved
            ? 'text-blue-600 bg-blue-50 hover:bg-blue-100'
            : 'text-gray-400 hover:text-blue-600 hover:bg-blue-50'
        }`}
        title={saved ? 'Saved' : 'Save for later'}
      >
        <svg
          className="w-5 h-5"
          fill={saved ? 'currentColor' : 'none'}
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
          />
        </svg>
      </button>

      <button
        onClick={handleDismiss}
        disabled={loading}
        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        title="Not interested"
      >
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
  );
}

/**
 * Spinner component for loading states
 */
function Spinner() {
  return (
    <svg
      className="animate-spin h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}
