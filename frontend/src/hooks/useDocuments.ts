'use client';

import { useRef, useMemo, useState, useEffect, useCallback } from 'react';

import { handleError } from 'src/utils/errorHandler';

import { fetcher, endpoints } from 'src/lib/axios';

// Types for documents data - matching backend API response
export interface DocumentItem {
  id: string; // Using name as id for frontend compatibility
  name: string;
  size: number;
  created_at: string;
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
      
      const response: DocumentItem[] = await fetcher(url);
      // Add id field using document name for frontend compatibility
      const documentsWithId = response.map(doc => ({
        ...doc,
        id: doc.name, // Use name as id for frontend compatibility
      }));
      setData(documentsWithId);
      setTotal(documentsWithId.length);
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

// TODO: These hooks will be implemented when backend endpoints are available:
// - useDocument (for document details)
// - useDocumentStats (for document statistics) 
// - useDocumentOperations (for delete/reindex operations)
// - useDocumentsHealth (for health checks)

// Placeholder hook for document operations - not implemented yet
export function useDocumentOperations() {
  const deleteDocument = async (documentId: string): Promise<void> => {
    // TODO: Implement when backend delete endpoint is available
    throw new Error('Delete operation not yet implemented');
  };

  const reindexDocument = async (documentId: string): Promise<void> => {
    // TODO: Implement when backend reindex endpoint is available
    throw new Error('Reindex operation not yet implemented');
  };

  return {
    deleteDocument,
    reindexDocument,
    loading: false,
    error: null,
  };
}
