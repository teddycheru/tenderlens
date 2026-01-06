import { useState, useEffect, useCallback } from 'react';
import { tenderApi } from '@/lib/tenders';
import type { Tender, TenderFilters, TenderListResponse } from '@/types/tender';

/**
 * Hook for fetching a list of tenders
 */
export function useTenders(filters?: TenderFilters) {
  const [data, setData] = useState<TenderListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTenders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await tenderApi.getTenders(filters);
      setData(response);
    } catch (err: any) {
      console.error('Error fetching tenders:', err);
      setError(err.response?.data?.detail || 'Failed to fetch tenders');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchTenders();
  }, [fetchTenders]);

  return { data, loading, error };
}

/**
 * Hook for fetching a single tender
 */
export function useTender(id: string) {
  const [tender, setTender] = useState<Tender | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTender = useCallback(async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);
      const response = await tenderApi.getTenderById(id);
      setTender(response);
    } catch (err: any) {
      console.error('Error fetching tender:', err);
      setError(err.response?.data?.detail || 'Failed to fetch tender');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchTender();
  }, [fetchTender]);

  return {
    tender,
    loading,
    error,
    refetch: fetchTender,
  };
}
