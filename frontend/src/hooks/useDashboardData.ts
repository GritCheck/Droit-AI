'use client';

import { useMemo, useState, useEffect, useCallback } from 'react';

import { handleError } from 'src/utils/errorHandler';

import { fetcher, endpoints } from 'src/lib/axios';

// Types for dashboard data matching API response
export interface TrendDataPoint {
  date: string;
  count?: number;
  score?: number;
}

export interface DashboardSummary {
  total_contracts_audited: number;
  avg_cost_per_audit_tokens: number;
  groundedness_rate: number;
  audit_success_rate: number;
}

export interface RiskAlerts {
  high_risk_clauses_detected: number;
  compliance_issues: number;
  critical_findings: number;
}

export interface PerformanceMetrics {
  avg_response_time_ms: number;
  cost_efficiency_score: number;
  token_utilization_rate: number;
}

export interface TrendAnalysis {
  daily_audits: TrendDataPoint[];
  groundedness_trend: TrendDataPoint[];
}

export interface ComplianceBreakdown {
  fully_compliant: number;
  partially_compliant: number;
  non_compliant: number;
  total_reviewed: number;
  compliance_rate: number;
}

export interface DashboardOverview {
  summary: DashboardSummary;
  risk_alerts: RiskAlerts;
  performance_metrics: PerformanceMetrics;
  trend_analysis: TrendAnalysis;
  compliance_breakdown: ComplianceBreakdown;
  data_source: string;
  last_updated: string;
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
      
      const response = await fetcher(endpoints.dashboard.managementOverview);
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
