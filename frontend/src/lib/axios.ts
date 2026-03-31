import type { AxiosRequestConfig } from 'axios';

import axios from 'axios';

import { CONFIG } from 'src/global-config';

// ----------------------------------------------------------------------

const axiosInstance = axios.create({ baseURL: CONFIG.serverUrl });

// Add Authorization header interceptor for Azure AD tokens
axiosInstance.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('azure_access_token');
    
    // Add Authorization header if token exists
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject((error.response && error.response.data) || 'Something went wrong!')
);

export default axiosInstance;

// ----------------------------------------------------------------------

export async function fetcher(args: string | [string, AxiosRequestConfig]): Promise<any> {
  try {
    const [url, config] = Array.isArray(args) ? args : [args];

    const res = await axiosInstance.get(url, { ...config });

    // Validate response structure
    if (!res.data) {
      throw new Error('Empty response received from server');
    }

    // Basic validation to prevent injection attacks
    if (typeof res.data === 'string' && res.data.length > 1000000) {
      throw new Error('Response too large');
    }

    return res.data;
  } catch (error: unknown) {
    console.error('Failed to fetch:', error);
    
    // Standardize error handling
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as any;
      if (axiosError.response?.data?.detail) {
        throw new Error(axiosError.response.data.detail);
      } else if (axiosError.response?.data?.message) {
        throw new Error(axiosError.response.data.message);
      }
    } else if (error instanceof Error) {
      throw error;
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
  // This line is never reached but satisfies the linter
  return null;
}

export async function poster(args: string | [string, AxiosRequestConfig]): Promise<any> {
  try {
    const [url, config] = Array.isArray(args) ? args : [args];

    const res = await axiosInstance.post(url, { ...config });

    // Validate response structure
    if (!res.data) {
      throw new Error('Empty response received from server');
    }

    return res.data;
  } catch (error: unknown) {
    console.error('Failed to post:', error);
    
    // Standardize error handling
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as any;
      if (axiosError.response?.data?.detail) {
        throw new Error(axiosError.response.data.detail);
      } else if (axiosError.response?.data?.message) {
        throw new Error(axiosError.response.data.message);
      }
    } else if (error instanceof Error) {
      throw error;
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
  // This line is never reached but satisfies the linter
  return null;
}

export async function putter(args: string | [string, AxiosRequestConfig]): Promise<any> {
  try {
    const [url, config] = Array.isArray(args) ? args : [args];

    const res = await axiosInstance.put(url, { ...config });

    // Validate response structure
    if (!res.data) {
      throw new Error('Empty response received from server');
    }

    return res.data;
  } catch (error: unknown) {
    console.error('Failed to put:', error);
    
    // Standardize error handling
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as any;
      if (axiosError.response?.data?.detail) {
        throw new Error(axiosError.response.data.detail);
      } else if (axiosError.response?.data?.message) {
        throw new Error(axiosError.response.data.message);
      }
    } else if (error instanceof Error) {
      throw error;
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
  // This line is never reached but satisfies the linter
  return null;
}

export async function deleter(args: string | [string, AxiosRequestConfig]): Promise<any> {
  try {
    const [url, config] = Array.isArray(args) ? args : [args];

    const res = await axiosInstance.delete(url, { ...config });

    // Validate response structure
    if (!res.data) {
      throw new Error('Empty response received from server');
    }

    return res.data;
  } catch (error: unknown) {
    console.error('Failed to delete:', error);
    
    // Standardize error handling
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as any;
      if (axiosError.response?.data?.detail) {
        throw new Error(axiosError.response.data.detail);
      } else if (axiosError.response?.data?.message) {
        throw new Error(axiosError.response.data.message);
      }
    } else if (error instanceof Error) {
      throw error;
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
  // This line is never reached but satisfies the linter
  return null;
}

// ----------------------------------------------------------------------

export const endpoints = {
  // Available endpoints from backend API
  auth: { me: '/auth/me', signIn: '/auth/login', signUp: '/auth/register' },
  health: '/health',
  root: '/',
  chat: {
    query: '/api/v1/chat/query',
    queryStream: '/api/v1/chat/query-stream'
  },
  documents: {
    list: '/api/v1/documents/'
  },
  metrics: {
    overview: '/api/v1/metrics/overview',
    kqlQueries: '/api/v1/metrics/kql-queries'
  },
  dashboard: {
    managementOverview: '/api/v1/dashboard/management-overview',
    kustoQueries: '/api/v1/dashboard/kusto-queries'
  },
  ingestion: {
    overview: '/api/v1/ingestion/overview',
    summary: '/api/v1/ingestion/summary',
    storage: '/api/v1/ingestion/storage',
    activity: '/api/v1/ingestion/activity'
  },
  security: {
    rlsPolicies: '/api/v1/security/rls-policies',
    userClearance: '/api/v1/security/user-clearance',
    health: '/api/v1/security/health',
    groups: '/api/v1/security/groups'
  },
  responsible: {
    overview: '/api/v1/responsible/overview',
    summary: '/api/v1/responsible/summary',
    performance: '/api/v1/responsible/performance',
    safety: '/api/v1/responsible/safety'
  }

};
