'use client';

import { useState, useEffect } from 'react';

import { fetcher, endpoints } from 'src/lib/axios';

// Types for security groups data
export interface SecurityGroup {
  id: string;
  title: string;
  subheader: string;
  filter: string;
  clearanceLevel: number;
  description: string;
  members: number;
  created: string;
  modified: string;
}

export interface RLSPolicy {
  id: string;
  name: string;
  description: string;
  isActive: boolean;
  priority: number;
  conditions: string;
}

export interface UserClearance {
  userId: string;
  clearanceLevel: number;
  groups: string[];
  department: string;
  lastUpdated: string;
}

export interface UseSecurityGroupsReturn {
  data: SecurityGroup[] | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useSecurityGroups(): UseSecurityGroupsReturn {
  const [data, setData] = useState<SecurityGroup[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.security.groups);
      setData(response.groups);
    } catch (err) {
      console.error('Failed to fetch security groups:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch security groups');
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

// Hook for RLS policies
export function useRLSPolicies() {
  const [data, setData] = useState<RLSPolicy[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPolicies = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.security.rlsPolicies);
      setData(response.policies);
    } catch (err) {
      console.error('Failed to fetch RLS policies:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch RLS policies');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  return { data, loading, error, refetch: fetchPolicies };
}

// Hook for user clearance
export function useUserClearance() {
  const [data, setData] = useState<UserClearance | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchClearance = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.security.userClearance);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch user clearance:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch user clearance');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClearance();
  }, []);

  return { data, loading, error, refetch: fetchClearance };
}

// Hook for security health check
export function useSecurityHealth() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetcher(endpoints.security.health);
      setData(response);
    } catch (err) {
      console.error('Failed to fetch security health:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch security health');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return { data, loading, error, refetch: fetchHealth };
}
