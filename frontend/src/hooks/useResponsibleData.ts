'use client';

import { useState, useEffect } from 'react';

import { fetcher, endpoints } from 'src/lib/axios';

// Types for responsible AI data
export interface ResponsibleSummary {
  totalAssertions: number;
  safetyFiltered: number;
  highConfidenceCitations: number;
}

export interface GroundednessData {
  title: string;
  total: number;
  percent: number;
  chart: {
    categories: string[];
    series: Array<{ data: number[] }>;
  };
}

export interface ReliabilityData {
  title: string;
  data: Array<{
    value: number;
    status: string;
    quantity: number;
  }>;
}

export interface SafetyCheckData {
  chart: {
    series: Array<{
      label: string;
      percent: number;
      total: number;
    }>;
  };
}

export interface PerformanceData {
  title: string;
  chart: {
    series: Array<{
      name: string;
      categories: string[];
      data: Array<{
        name: string;
        data: number[];
      }>;
    }>;
  };
}

export interface ModerationData {
  title: string;
  chart: {
    series: Array<{
      label: string;
      value: number;
    }>;
  };
}

export interface FeedbackItem {
  id: string;
  name: string;
  rating: number;
  tags: string[];
  avatarUrl: string;
  description: string;
  postedAt: string;
}

export interface InterventionItem {
  id: string;
  name: string;
  price: number;
  guests: string;
  isHot: boolean;
  duration: string;
  coverUrl: string;
  avatarUrl: string;
  bookedAt: string;
}

export interface AuditItem {
  id: string;
  status: string;
  checkIn: string;
  checkOut: string;
  destination: {
    name: string;
    coverUrl: string;
  };
  customer: {
    name: string;
    avatarUrl: string;
    phoneNumber: string;
  };
}

export interface FeedbackData {
  title: string;
  subheader: string;
  list: FeedbackItem[];
}

export interface InterventionsData {
  title: string;
  list: InterventionItem[];
}

export interface AuditData {
  title: string;
  headers: Array<{ id: string; label: string }>;
  tableData: AuditItem[];
}

export interface ResponsibleOverview {
  summary: ResponsibleSummary;
  groundedness: GroundednessData;
  reliability: ReliabilityData;
  safetyChecks: SafetyCheckData;
  performance: PerformanceData;
  moderation: ModerationData;
  feedback: FeedbackData;
  interventions: InterventionsData;
  audit: AuditData;
}

export interface UseResponsibleDataReturn {
  data: ResponsibleOverview | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useResponsibleData(): UseResponsibleDataReturn {
  const [data, setData] = useState<ResponsibleOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.responsible.overview);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch responsible AI data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch responsible AI data');
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
export function useResponsibleSummary() {
  const [data, setData] = useState<ResponsibleSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.responsible.summary);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch responsible AI summary:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch responsible AI summary');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  return { data, loading, error, refetch: fetchSummary };
}

export function usePerformanceMetrics() {
  const [data, setData] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPerformance = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.responsible.performance);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch performance metrics:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch performance metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPerformance();
  }, []);

  return { data, loading, error, refetch: fetchPerformance };
}

export function useSafetyMetrics() {
  const [data, setData] = useState<{
    groundedness: GroundednessData;
    reliability: ReliabilityData;
    safetyChecks: SafetyCheckData;
    moderation: ModerationData;
  } | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSafety = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.responsible.safety);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch safety metrics:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch safety metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSafety();
  }, []);

  return { data, loading, error, refetch: fetchSafety };
}
