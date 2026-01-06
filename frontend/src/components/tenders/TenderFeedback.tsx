/**
 * Tender feedback component
 * Allows users to rate tenders and provide feedback
 */

import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TenderFeedbackProps {
  tenderId: string;
  onPositive: (reason?: string) => void;
  onNegative: (reason?: string) => void;
  onDismiss?: (reason?: string) => void;
  compact?: boolean;
}

const POSITIVE_REASONS = [
  'Perfect match for our expertise',
  'Good budget range',
  'Preferred location',
  'Interesting opportunity'
];

const NEGATIVE_REASONS = [
  'Not in our sector',
  'Budget too low/high',
  'Wrong location',
  'Deadline too soon',
  'Missing required qualifications'
];

export function TenderFeedback({
  tenderId,
  onPositive,
  onNegative,
  onDismiss,
  compact = false
}: TenderFeedbackProps) {
  const [showReasons, setShowReasons] = useState<'positive' | 'negative' | null>(null);
  const [customReason, setCustomReason] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handlePositive = (reason?: string) => {
    onPositive(reason);
    setSubmitted(true);
    setTimeout(() => setShowReasons(null), 1000);
  };

  const handleNegative = (reason?: string) => {
    onNegative(reason);
    setSubmitted(true);
    setTimeout(() => setShowReasons(null), 1000);
  };

  if (submitted) {
    return (
      <div className="text-sm text-green-600 font-medium">
        ✓ Feedback recorded - Thank you!
      </div>
    );
  }

  if (showReasons) {
    const reasons = showReasons === 'positive' ? POSITIVE_REASONS : NEGATIVE_REASONS;
    const handler = showReasons === 'positive' ? handlePositive : handleNegative;

    return (
      <div className="space-y-2 p-3 bg-gray-50 rounded-lg border">
        <div className="flex justify-between items-center">
          <p className="text-sm font-medium text-gray-700">
            {showReasons === 'positive' ? 'Why is this a good match?' : 'Why is this not relevant?'}
          </p>
          <button
            onClick={() => setShowReasons(null)}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-1">
          {reasons.map((reason) => (
            <button
              key={reason}
              onClick={() => handler(reason)}
              className="w-full text-left text-xs px-3 py-2 rounded bg-white hover:bg-blue-50 border hover:border-blue-200 transition-colors"
            >
              {reason}
            </button>
          ))}

          <div className="flex gap-2 mt-2">
            <input
              type="text"
              placeholder="Other reason..."
              value={customReason}
              onChange={(e) => setCustomReason(e.target.value)}
              className="flex-1 text-xs px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && customReason.trim()) {
                  handler(customReason);
                }
              }}
            />
            <button
              onClick={() => customReason.trim() && handler(customReason)}
              disabled={!customReason.trim()}
              className="px-3 py-2 text-xs bg-blue-600 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
            >
              Submit
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('flex items-center gap-2', compact ? 'gap-1' : 'gap-2')}>
      <button
        onClick={() => setShowReasons('positive')}
        className={cn(
          'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-gray-200 hover:border-green-300 hover:bg-green-50 transition-colors group',
          compact && 'px-2 py-1'
        )}
        title="Good match"
      >
        <ThumbsUp className={cn('text-gray-400 group-hover:text-green-600', compact ? 'w-3.5 h-3.5' : 'w-4 h-4')} />
        {!compact && <span className="text-xs text-gray-600 group-hover:text-green-700">Good match</span>}
      </button>

      <button
        onClick={() => setShowReasons('negative')}
        className={cn(
          'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-gray-200 hover:border-red-300 hover:bg-red-50 transition-colors group',
          compact && 'px-2 py-1'
        )}
        title="Not relevant"
      >
        <ThumbsDown className={cn('text-gray-400 group-hover:text-red-600', compact ? 'w-3.5 h-3.5' : 'w-4 h-4')} />
        {!compact && <span className="text-xs text-gray-600 group-hover:text-red-700">Not relevant</span>}
      </button>

      {onDismiss && (
        <button
          onClick={() => onDismiss()}
          className={cn(
            'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-colors group',
            compact && 'px-2 py-1'
          )}
          title="Hide this tender"
        >
          <X className={cn('text-gray-400 group-hover:text-gray-600', compact ? 'w-3.5 h-3.5' : 'w-4 h-4')} />
          {!compact && <span className="text-xs text-gray-600 group-hover:text-gray-700">Hide</span>}
        </button>
      )}
    </div>
  );
}
