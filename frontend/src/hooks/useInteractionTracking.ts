/**
 * Hook for tracking user interactions with tenders
 * Automatically tracks view time and provides methods for other interactions
 */

import { useEffect, useRef, useCallback } from 'react';
import { InteractionType } from '@/types/interaction';

interface UseInteractionTrackingOptions {
  tenderId: string;
  enabled?: boolean;
}

export function useInteractionTracking({
  tenderId,
  enabled = true
}: UseInteractionTrackingOptions) {
  const startTime = useRef<number>(Date.now());
  const tracked = useRef<boolean>(false);

  // Track interaction with backend
  const trackInteraction = useCallback(
    async (type: InteractionType, timeSpent?: number, feedbackReason?: string) => {
      if (!enabled) return;

      try {
        const response = await fetch('/api/v1/interactions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // TODO: Add auth token from context
          },
          body: JSON.stringify({
            tender_id: tenderId,
            interaction_type: type,
            time_spent_seconds: timeSpent,
            feedback_reason: feedbackReason
          })
        });

        if (!response.ok) {
          console.error('Failed to track interaction:', response.statusText);
        }
      } catch (error) {
        console.error('Error tracking interaction:', error);
      }
    },
    [tenderId, enabled]
  );

  // Track view on mount and time spent on unmount
  useEffect(() => {
    if (!enabled || tracked.current) return;

    startTime.current = Date.now();

    return () => {
      if (!tracked.current) {
        const timeSpent = Math.floor((Date.now() - startTime.current) / 1000);

        // Only track views longer than 5 seconds
        if (timeSpent >= 5) {
          trackInteraction('view', timeSpent);
          tracked.current = true;
        }
      }
    };
  }, [tenderId, enabled, trackInteraction]);

  // Convenience methods for different interaction types
  const trackSave = useCallback(() => {
    return trackInteraction('save');
  }, [trackInteraction]);

  const trackApply = useCallback(() => {
    return trackInteraction('apply');
  }, [trackInteraction]);

  const trackDismiss = useCallback((reason?: string) => {
    return trackInteraction('dismiss', undefined, reason);
  }, [trackInteraction]);

  const trackPositiveRating = useCallback((reason?: string) => {
    return trackInteraction('rate_positive', undefined, reason);
  }, [trackInteraction]);

  const trackNegativeRating = useCallback((reason?: string) => {
    return trackInteraction('rate_negative', undefined, reason);
  }, [trackInteraction]);

  return {
    trackSave,
    trackApply,
    trackDismiss,
    trackPositiveRating,
    trackNegativeRating,
    trackInteraction
  };
}
