'use client';

import { useState, useEffect, useCallback } from 'react';
import { Sparkles } from 'lucide-react';

interface AIQuickScanProps {
  summary?: string;
  isProcessed: boolean;
  tenderId: string;
}

export default function AIQuickScan({ summary, isProcessed, tenderId }: AIQuickScanProps) {
  const [quickScan, setQuickScan] = useState<string>(summary || '');
  const [loading, setLoading] = useState(!isProcessed);

  const fetchAIStatus = useCallback(async () => {
    try {
      const { aiApi } = await import('@/lib/ai');
      const response = await aiApi.getAIStatus(tenderId);

      if (response.has_summary) {
        const result = await aiApi.getAIResults(tenderId);
        if (result.quick_scan) {
          setQuickScan(result.quick_scan);
          setLoading(false);
        }
      }
    } catch (error) {
      console.error('Failed to fetch AI status:', error);
      setLoading(false);
    }
  }, [tenderId]);

  useEffect(() => {
    if (!isProcessed && !summary) {
      fetchAIStatus();
    }
  }, [isProcessed, summary, fetchAIStatus]);

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Sparkles className="h-4 w-4 animate-pulse text-blue-500" />
        <span className="italic">AI processing...</span>
      </div>
    );
  }

  if (!quickScan) {
    return null;
  }

  return (
    <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800">
      <div className="flex items-start gap-2">
        <Sparkles className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <span className="text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-wide">
            AI Quick Scan
          </span>
          <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">{quickScan}</p>
        </div>
      </div>
    </div>
  );
}
