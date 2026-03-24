'use client';

import { useState, useEffect } from 'react';

import { fetcher, endpoints } from 'src/lib/axios';

// Types for ingestion data
export interface IngestionSummary {
  title: string;
  value: number;
  total: number;
  icon: string;
}

export interface StorageCategory {
  name: string;
  usedStorage: number;
  filesCount: number;
  icon: string;
}

export interface StorageOverview {
  totalGB: number;
  usedPercent: number;
  categories: StorageCategory[];
}

export interface ChartDataPoint {
  name: string;
  data: number[];
}

export interface ChartSeries {
  name: string;
  categories: string[];
  data: ChartDataPoint[];
}

export interface IngestionActivity {
  chartSeries: ChartSeries[];
}

export interface Folder {
  id: string;
  name: string;
  type: string;
  size: number;
  modified: string;
  modifiedAt: string;
  url: string;
  tags: string[];
  isFavorited: boolean;
  createdAt: string;
  shared: Array<{
    id: string;
    name: string;
    email: string;
    avatarUrl: string;
    permission: string;
  }>;
  permission: string;
}

export interface RecentFile {
  id: string;
  name: string;
  type: string;
  size: number;
  modified: string;
  modifiedAt: string;
  url: string;
  tags: string[];
  isFavorited: boolean;
  createdAt: string;
  shared: Array<{
    id: string;
    name: string;
    email: string;
    avatarUrl: string;
    permission: string;
  }>;
  permission: string;
}

export interface IngestionOverview {
  summary: {
    adls: IngestionSummary;
    docling: IngestionSummary;
    aiSearch: IngestionSummary;
  };
  storage: StorageOverview;
  activity: IngestionActivity;
  folders: Folder[];
  recentFiles: RecentFile[];
}

export interface UseIngestionDataReturn {
  data: IngestionOverview | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useIngestionData(): UseIngestionDataReturn {
  const [data, setData] = useState<IngestionOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.ingestion.overview);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch ingestion data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch ingestion data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
}

// Individual hooks for specific data sections
export function useIngestionSummary() {
  const [data, setData] = useState<{
    adls: IngestionSummary;
    docling: IngestionSummary;
    aiSearch: IngestionSummary;
  } | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.ingestion.summary);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch ingestion summary:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch ingestion summary');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  return { data, loading, error, refetch: fetchSummary };
}

export function useStorageOverview() {
  const [data, setData] = useState<StorageOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStorage = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.ingestion.storage);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch storage overview:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch storage overview');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStorage();
  }, []);

  return { data, loading, error, refetch: fetchStorage };
}

export function useIngestionActivity() {
  const [data, setData] = useState<IngestionActivity | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchActivity = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.ingestion.activity);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch ingestion activity:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch ingestion activity');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivity();
  }, []);

  return { data, loading, error, refetch: fetchActivity };
}
