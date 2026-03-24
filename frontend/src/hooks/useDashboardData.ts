'use client';

import { useMemo, useState, useEffect, useCallback } from 'react';

import { handleError } from 'src/utils/errorHandler';

import { fetcher, endpoints } from 'src/lib/axios';

// Types for dashboard data
export interface DashboardStats {
  title: string;
  percent: number;
  total: number;
  categories: string[];
  series: number[];
}

export interface ChartSeries {
  label: string;
  value: number;
}

export interface VolumeSeries {
  name: string;
  data: Array<{ name: string; data: number[] }>;
}

export interface DashboardCharts {
  distribution: {
    title: string;
    subheader: string;
    series: ChartSeries[];
  };
  volume: {
    title: string;
    subheader: string;
    categories: string[];
    series: VolumeSeries[];
  };
}

export interface DashboardWidget {
  title: string;
  total: number;
  icon: string;
  series: number;
}

export interface DashboardWidgets {
  optimization: DashboardWidget;
  azureTokens: DashboardWidget;
}

export interface DashboardAudit {
  title: string;
  headers: Array<{ id: string; label: string }>;
}

export interface DashboardRecent {
  title: string;
  list: any[];
}

export interface DashboardWelcome {
  title: string;
  description: string;
  actionText: string;
  actionHref: string;
}

export interface DashboardOverview {
  welcome: DashboardWelcome;
  stats: {
    groundedness: DashboardStats;
    indexing: DashboardStats;
    compliance: DashboardStats;
  };
  charts: DashboardCharts;
  audit: DashboardAudit;
  widgets: DashboardWidgets;
  recent: DashboardRecent;
}

export interface UseDashboardDataReturn {
  data: DashboardOverview | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useDashboardData(): UseDashboardDataReturn {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useMemo(() => async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.dashboard.overview);
      setData(response);
    } catch (err) {
      setError(handleError(err, { 
        fallbackMessage: 'Failed to fetch dashboard data',
        context: 'Dashboard fetch'
      }));
    } finally {
      setLoading(false);
    }
  }, []);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch,
  };
}

// Individual hooks for specific data sections
export function useDashboardStats() {
  const [data, setData] = useState<{
    groundedness: DashboardStats;
    indexing: DashboardStats;
    compliance: DashboardStats;
  } | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.dashboard.stats);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch dashboard stats:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard stats');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return { data, loading, error, refetch: fetchStats };
}

export function useDashboardCharts() {
  const [data, setData] = useState<DashboardCharts | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCharts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.dashboard.charts);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch dashboard charts:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard charts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCharts();
  }, []);

  return { data, loading, error, refetch: fetchCharts };
}

export function useDashboardWidgets() {
  const [data, setData] = useState<DashboardWidgets | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWidgets = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.dashboard.widgets);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch dashboard widgets:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard widgets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWidgets();
  }, []);

  return { data, loading, error, refetch: fetchWidgets };
}
