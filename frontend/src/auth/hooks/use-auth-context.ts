'use client';

import { useContext } from 'react';

import { CONFIG } from 'src/global-config';
import { AuthContext } from '../context/auth-context';
import { useAzureAuth } from '../context/azure-auth-context';

// ----------------------------------------------------------------------

export function useAuthContext() {
  // Use Azure AD context if Azure auth is enabled
  if (CONFIG.auth.method === 'azure') {
    return useAzureAuth();
  }

  // Fall back to the original auth context for other methods
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuthContext: Context must be used inside AuthProvider');
  }

  return context;
}
