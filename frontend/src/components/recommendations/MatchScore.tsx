/**
 * MatchScore Component
 * Displays AI match score with visual badge and label
 */

import React from 'react';
import { getScoreLabel, getScoreBadgeClass } from '@/types/recommendation';

interface MatchScoreProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export default function MatchScore({
  score,
  size = 'md',
  showLabel = true,
  className = '',
}: MatchScoreProps) {
  const label = getScoreLabel(score);
  const badgeClass = getScoreBadgeClass(score);

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5',
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className={`${badgeClass} ${sizeClasses[size]}`}>
        {Math.round(score)}%
      </span>
      {showLabel && (
        <span className={`text-${size === 'sm' ? 'xs' : 'sm'} text-gray-600 font-medium`}>
          {label}
        </span>
      )}
    </div>
  );
}

/**
 * Circular progress score variant
 */
export function MatchScoreCircular({
  score,
  size = 60,
  className = '',
}: {
  score: number;
  size?: number;
  className?: string;
}) {
  const radius = size / 2 - 5;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getColor = (score: number) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#3b82f6'; // blue
    if (score >= 40) return '#eab308'; // yellow
    return '#6b7280'; // gray
  };

  return (
    <div className={`relative ${className}`} style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="4"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor(score)}
          strokeWidth="4"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500 ease-out"
        />
      </svg>
      {/* Score text */}
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-lg font-bold" style={{ color: getColor(score) }}>
          {Math.round(score)}%
        </span>
      </div>
    </div>
  );
}
