'use client';

import { useRef, useMemo, useState, useEffect, useCallback } from 'react';

import { handleError } from 'src/utils/errorHandler';

import { fetcher, endpoints } from 'src/lib/axios';

// Types for documents data - matching the mock structure
export interface DocumentItem {
  id: string;
  type: string;
  name: string;
  data_limit: string;
  time_limit: string;
  rate_limit: string;
  session_timeout: number;
  idle_timeout: number;
  price: number;
  status: string;
  validity_period: string;
  features: string;
  subscribers: number;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentFilters {
  name: string;
  type: string[];
  status: string;
}

export interface DocumentListResponse {
  documents: DocumentItem[];
  total: number;
  skip: number;
  limit: number;
  filters: {
    status?: string;
    type?: string;
    search?: string;
  };
}

export interface DocumentStats {
  total: number;
  by_status: {
    indexed: number;
    processing: number;
    failed: number;
    flagged: number;
  };
  by_type: Record<string, number>;
  by_security_level: Record<string, number>;
  total_subscribers: number;
}

export interface UseDocumentsReturn {
  data: DocumentItem[] | null;
  loading: boolean;
  refetching: boolean;
  error: string | null;
  total: number;
  refetch: () => void;
}

export function useDocuments(filters?: DocumentFilters) {
  const [data, setData] = useState<DocumentItem[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refetching, setRefetching] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState<number>(0);
  
  // Debouncing for search filters
  const debounceRef = useRef<NodeJS.Timeout>();
  const [debouncedFilters, setDebouncedFilters] = useState<DocumentFilters | undefined>(filters);

  // Debounce filter changes (especially for search) - fixed memory leak
  const updateDebouncedFilters = useCallback((newFilters: DocumentFilters | undefined) => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    
    debounceRef.current = setTimeout(() => {
      setDebouncedFilters(newFilters);
    }, 300); // 300ms debounce delay
  }, []);

  // Update debounced filters when input filters change
  useEffect(() => {
    updateDebouncedFilters(filters);
    
    // Cleanup function - only clear timeout on unmount
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [filters, updateDebouncedFilters]);

  const fetchData = useMemo(() => async (isRefetch = false) => {
    try {
      if (isRefetch) {
        setRefetching(true);
      } else {
        setLoading(true);
      }
      setError(null);
      
      // Build query parameters using debounced filters
      const params = new URLSearchParams();
      if (debouncedFilters?.status && debouncedFilters.status !== 'all') {
        params.append('status', debouncedFilters.status);
      }
      if (debouncedFilters?.type && debouncedFilters.type.length > 0) {
        // Send all types as comma-separated values
        params.append('type', debouncedFilters.type.join(','));
      }
      if (debouncedFilters?.name) {
        params.append('search', debouncedFilters.name);
      }
      
      const url = params.toString() 
        ? `${endpoints.documents.list}?${params.toString()}`
        : endpoints.documents.list;
      
      const response: DocumentListResponse = await fetcher(url);
      setData(response.documents);
      setTotal(response.total);
    } catch (err) {
      setError(handleError(err, { 
        fallbackMessage: 'Failed to fetch documents',
        context: 'Document fetch'
      }));
    } finally {
      setLoading(false);
      setRefetching(false);
    }
  }, [debouncedFilters?.status, debouncedFilters?.type, debouncedFilters?.name]);

  // Create refetch function that triggers refetching state
  const refetch = useCallback(() => {
    fetchData(true);
  }, [fetchData]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    refetching,
    error,
    total,
    refetch,
  };
}

// Hook for document details
export function useDocument(documentId: string) {
  const [data, setData] = useState<DocumentItem | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocument = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const url = endpoints.documents.detail.replace('{id}', documentId);
      const response: DocumentItem = await fetcher(url);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch document:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch document');
    } finally {
      setLoading(false);
    }
  }, [documentId]);

  useEffect(() => {
    if (documentId) {
      fetchDocument();
    }
  }, [documentId, fetchDocument]);

  return {
    data,
    loading,
    error,
    refetch: fetchDocument,
  };
}

// Hook for document statistics
export function useDocumentStats() {
  const [data, setData] = useState<DocumentStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response: DocumentStats = await fetcher(endpoints.documents.stats);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch document stats:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch document stats');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return {
    data,
    loading,
    error,
    refetch: fetchStats,
  };
}

// Hook for document operations (delete, reindex)
export function useDocumentOperations() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const deleteDocument = async (documentId: string): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      const url = endpoints.documents.delete.replace('{id}', documentId);
      await fetcher(url);
    } catch (err) {
      console.error('Failed to delete document:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete document');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reindexDocument = async (documentId: string): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      const url = endpoints.documents.reindex.replace('{id}', documentId);
      await fetcher(url);
    } catch (err) {
      console.error('Failed to reindex document:', err);
      setError(err instanceof Error ? err.message : 'Failed to reindex document');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    deleteDocument,
    reindexDocument,
    loading,
    error,
  };
}

// Hook for documents health check
export function useDocumentsHealth() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.documents.health);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch documents health:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch documents health');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return { data, loading, error, refetch: fetchHealth };
}
