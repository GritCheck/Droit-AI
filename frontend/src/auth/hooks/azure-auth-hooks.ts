'use client';

import { useCallback } from 'react';

import { CONFIG } from 'src/global-config';

import { useAzureAuth } from '../context/azure-auth-context';

// ----------------------------------------------------------------------

export function useAuthUser() {
  const { user, loading, authenticated, unauthenticated } = useAzureAuth();

  return {
    user,
    loading,
    authenticated,
    unauthenticated,
  };
}

// ----------------------------------------------------------------------

export function useAuthContext() {
  const { 
    user, 
    loading, 
    authenticated, 
    unauthenticated, 
    checkUserSession, 
    login, 
    logout, 
    getAccessToken 
  } = useAzureAuth();

  return {
    user,
    loading,
    authenticated,
    unauthenticated,
    checkUserSession,
    login,
    logout,
    getAccessToken,
  };
}

// ----------------------------------------------------------------------

export function useMockedUser() {
  // For development/testing - fallback to mock user if Azure auth is disabled
  const { user, loading } = useAuthUser();

  if (CONFIG.auth.skip || !CONFIG.azure.clientId) {
    return {
      id: 'mock-user-id',
      displayName: 'Test User',
      email: 'test@droitai.com',
      role: 'admin',
      photoURL: '/assets/mock-avatar.png',
    };
  }

  return user || {
    id: '',
    displayName: '',
    email: '',
    role: '',
    photoURL: '',
  };
}

// ----------------------------------------------------------------------

export function useSignOut() {
  const { logout } = useAzureAuth();

  const handleSignOut = useCallback(async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Sign out failed:', error);
    }
  }, [logout]);

  return handleSignOut;
}

// ----------------------------------------------------------------------

export function useSignIn() {
  const { login } = useAzureAuth();

  const handleSignIn = useCallback(async () => {
    try {
      await login();
    } catch (error) {
      console.error('Sign in failed:', error);
    }
  }, [login]);

  return handleSignIn;
}

// ----------------------------------------------------------------------

export function useGetAccessToken() {
  const { getAccessToken } = useAzureAuth();

  return getAccessToken;
}
