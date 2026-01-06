/**
 * Relevance score badge component for tender cards
 * Displays the match percentage with color coding
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { getScoreColor, getScoreLabel } from '@/types/recommendation';

interface RelevanceScoreProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function RelevanceScore({
  score,
  size = 'md',
  showLabel = false,
  className
}: RelevanceScoreProps) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5'
  };

  const colorClasses = getScoreColor(score);
  const label = getScoreLabel(score);

  return (
    <div className={cn('inline-flex items-center gap-1.5', className)}>
      <div
        className={cn(
          'rounded-full font-semibold',
          sizeClasses[size],
          colorClasses
        )}
        title={`${score}% Match - ${label}`}
      >
        {Math.round(score)}%
      </div>
      {showLabel && (
        <span className="text-xs text-gray-500 font-medium">{label}</span>
      )}
    </div>
  );
}
