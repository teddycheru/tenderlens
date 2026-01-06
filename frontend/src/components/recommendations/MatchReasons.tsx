/**
 * MatchReasons Component
 * Displays explainable AI match reasons with icons and weights
 */

import React from 'react';
import { MatchReason, REASON_TYPE_ICONS, REASON_TYPE_LABELS } from '@/types/recommendation';

interface MatchReasonsProps {
  reasons: MatchReason[];
  variant?: 'compact' | 'detailed';
  maxVisible?: number;
  showWeights?: boolean;
  className?: string;
}

export default function MatchReasons({
  reasons,
  variant = 'detailed',
  maxVisible,
  showWeights = true,
  className = '',
}: MatchReasonsProps) {
  const visibleReasons = maxVisible ? reasons.slice(0, maxVisible) : reasons;
  const hiddenCount = maxVisible && reasons.length > maxVisible ? reasons.length - maxVisible : 0;

  if (reasons.length === 0) {
    return null;
  }

  return (
    <div className={className}>
      {variant === 'compact' ? (
        <CompactView reasons={visibleReasons} showWeights={showWeights} />
      ) : (
        <DetailedView reasons={visibleReasons} showWeights={showWeights} />
      )}

      {hiddenCount > 0 && (
        <div className="mt-2 text-xs text-gray-500">
          +{hiddenCount} more reason{hiddenCount > 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
}

/**
 * Compact view - horizontal pills
 */
function CompactView({ reasons, showWeights }: { reasons: MatchReason[]; showWeights: boolean }) {
  return (
    <div className="flex flex-wrap gap-2">
      {reasons.map((reason, idx) => (
        <div
          key={idx}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-gray-50 border border-gray-200 rounded-full text-xs"
        >
          <span>{REASON_TYPE_ICONS[reason.type]}</span>
          <span className="font-medium text-gray-700">
            {REASON_TYPE_LABELS[reason.type]}
          </span>
          {showWeights && (
            <span className="text-gray-500">
              +{Math.round(reason.weight)}pts
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

/**
 * Detailed view - vertical list with descriptions
 */
function DetailedView({ reasons, showWeights }: { reasons: MatchReason[]; showWeights: boolean }) {
  return (
    <div className="space-y-2">
      {reasons.map((reason, idx) => (
        <div
          key={idx}
          className="flex items-start gap-3 p-3 bg-gray-50 border border-gray-200 rounded-lg"
        >
          <div className="flex-shrink-0 text-2xl">
            {REASON_TYPE_ICONS[reason.type]}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="text-sm font-semibold text-gray-900">
                {REASON_TYPE_LABELS[reason.type]}
              </h4>
              {reason.category && (
                <span className="text-xs text-gray-500">
                  • {reason.category}
                </span>
              )}
            </div>

            <p className="text-sm text-gray-600">
              {reason.reason}
            </p>
          </div>

          {showWeights && (
            <div className="flex-shrink-0 text-right">
              <div className="text-sm font-bold text-blue-600">
                +{Math.round(reason.weight)}
              </div>
              <div className="text-xs text-gray-500">
                pts
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/**
 * Grouped view - reasons grouped by category
 */
export function MatchReasonsGrouped({
  reasons,
  showWeights = true,
  className = '',
}: {
  reasons: MatchReason[];
  showWeights?: boolean;
  className?: string;
}) {
  // Group reasons by type
  const grouped = reasons.reduce((acc, reason) => {
    if (!acc[reason.type]) {
      acc[reason.type] = [];
    }
    acc[reason.type].push(reason);
    return acc;
  }, {} as Record<string, MatchReason[]>);

  return (
    <div className={`space-y-3 ${className}`}>
      {Object.entries(grouped).map(([type, typeReasons]) => {
        const totalWeight = typeReasons.reduce((sum, r) => sum + r.weight, 0);

        return (
          <div key={type} className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 bg-gray-100 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <span className="text-xl">
                  {REASON_TYPE_ICONS[type as keyof typeof REASON_TYPE_ICONS]}
                </span>
                <span className="text-sm font-semibold text-gray-900">
                  {REASON_TYPE_LABELS[type as keyof typeof REASON_TYPE_LABELS]}
                </span>
                <span className="text-xs text-gray-500">
                  ({typeReasons.length})
                </span>
              </div>

              {showWeights && (
                <div className="text-sm font-bold text-blue-600">
                  +{Math.round(totalWeight)} pts
                </div>
              )}
            </div>

            <div className="p-3 space-y-2">
              {typeReasons.map((reason, idx) => (
                <div key={idx} className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    {reason.category && (
                      <div className="text-xs font-medium text-gray-700 mb-0.5">
                        {reason.category}
                      </div>
                    )}
                    <div className="text-sm text-gray-600">
                      {reason.reason}
                    </div>
                  </div>

                  {showWeights && typeReasons.length > 1 && (
                    <div className="flex-shrink-0 text-xs text-gray-500">
                      +{Math.round(reason.weight)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Summary view - just counts and total score
 */
export function MatchReasonsSummary({
  reasons,
  className = '',
}: {
  reasons: MatchReason[];
  className?: string;
}) {
  const totalWeight = reasons.reduce((sum, r) => sum + r.weight, 0);
  const typeCounts = reasons.reduce((acc, r) => {
    acc[r.type] = (acc[r.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="flex gap-1.5">
        {Object.entries(typeCounts).map(([type, count]) => (
          <div
            key={type}
            className="flex items-center gap-0.5 text-xs text-gray-600"
            title={REASON_TYPE_LABELS[type as keyof typeof REASON_TYPE_LABELS]}
          >
            <span>{REASON_TYPE_ICONS[type as keyof typeof REASON_TYPE_ICONS]}</span>
            {count > 1 && <span className="font-medium">×{count}</span>}
          </div>
        ))}
      </div>

      <div className="text-xs text-gray-400">•</div>

      <div className="text-xs font-semibold text-blue-600">
        {Math.round(totalWeight)} pts total
      </div>
    </div>
  );
}
