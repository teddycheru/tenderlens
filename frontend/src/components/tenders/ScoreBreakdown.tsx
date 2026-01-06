/**
 * Score breakdown tooltip/popover component
 * Shows detailed explanation of how the relevance score was calculated
 */

import React from 'react';
import { ScoreBreakdown as ScoreBreakdownType } from '@/types/recommendation';
import { CheckCircle, XCircle, Info } from 'lucide-react';

interface ScoreBreakdownProps {
  breakdown: ScoreBreakdownType;
  explanation?: string;
}

export function ScoreBreakdown({ breakdown, explanation }: ScoreBreakdownProps) {
  const scoreItems = [];

  // Category match
  if (breakdown.category?.matched) {
    scoreItems.push({
      label: 'Category Match',
      value: `+${breakdown.category.points}`,
      detail: breakdown.category.type,
      matched: true
    });
  }

  // Region match
  if (breakdown.region?.matched) {
    scoreItems.push({
      label: 'Region',
      value: `+${breakdown.region.points}`,
      detail: breakdown.region.value,
      matched: true
    });
  }

  // Budget match
  if (breakdown.budget?.matched) {
    scoreItems.push({
      label: 'Budget in Range',
      value: `+${breakdown.budget.points}`,
      detail: `${breakdown.budget.value?.toLocaleString()} ETB`,
      matched: true
    });
  }

  // Keywords
  if (breakdown.keywords && breakdown.keywords.matched.length > 0) {
    scoreItems.push({
      label: 'Matching Keywords',
      value: `+${breakdown.keywords.points}`,
      detail: breakdown.keywords.matched.slice(0, 3).join(', '),
      matched: true
    });
  }

  // Certifications
  if (breakdown.certifications && breakdown.certifications.matched.length > 0) {
    scoreItems.push({
      label: 'Required Certifications',
      value: `+${breakdown.certifications.points}`,
      detail: breakdown.certifications.matched.join(', '),
      matched: true
    });
  }

  // Language
  if (breakdown.language?.matched) {
    scoreItems.push({
      label: 'Language',
      value: `+${breakdown.language.points}`,
      matched: true
    });
  }

  // Deadline
  if (breakdown.deadline?.matched) {
    scoreItems.push({
      label: 'Deadline',
      value: `+${breakdown.deadline.points}`,
      detail: `${breakdown.deadline.days} days remaining`,
      matched: true
    });
  }

  return (
    <div className="w-80 p-4 space-y-3">
      {/* Header */}
      <div>
        <h4 className="font-semibold text-sm mb-1">Match Breakdown</h4>
        <p className="text-xs text-gray-500">
          This tender scored <span className="font-semibold">{Math.round(breakdown.rule_score + breakdown.semantic_score)}%</span> based on your profile
        </p>
      </div>

      {/* Score Components */}
      <div className="space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="text-gray-600">Rule-based score</span>
          <span className="font-medium">{Math.round(breakdown.rule_score)}%</span>
        </div>
        <div className="flex justify-between items-center text-xs">
          <span className="text-gray-600">Content similarity</span>
          <span className="font-medium">{Math.round(breakdown.semantic_score)}%</span>
        </div>
        {breakdown.popularity_score !== undefined && breakdown.popularity_score > 0 && (
          <div className="flex justify-between items-center text-xs">
            <span className="text-gray-600">Popularity boost</span>
            <span className="font-medium">+{Math.round(breakdown.popularity_score)}%</span>
          </div>
        )}
      </div>

      {/* Matching Criteria */}
      {scoreItems.length > 0 && (
        <>
          <div className="border-t pt-2">
            <p className="text-xs font-medium text-gray-700 mb-2">Matching Criteria:</p>
            <div className="space-y-1.5">
              {scoreItems.map((item, index) => (
                <div key={index} className="flex items-start gap-2 text-xs">
                  <CheckCircle className="w-3.5 h-3.5 text-green-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start gap-2">
                      <span className="text-gray-700">{item.label}</span>
                      <span className="text-green-600 font-medium flex-shrink-0">{item.value}</span>
                    </div>
                    {item.detail && (
                      <p className="text-gray-500 text-xs truncate">{item.detail}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Explanation */}
      {explanation && (
        <div className="border-t pt-2">
          <div className="flex items-start gap-2">
            <Info className="w-3.5 h-3.5 text-blue-600 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-gray-600">{explanation}</p>
          </div>
        </div>
      )}
    </div>
  );
}
