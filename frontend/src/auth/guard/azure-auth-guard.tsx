'use client';

import type { ReactNode } from 'react';

import { paths } from 'src/routes/paths';
import { useRouter } from 'src/routes/hooks';

import { useAuthContext } from '../hooks/azure-auth-hooks';

// ----------------------------------------------------------------------

type AzureAuthGuardProps = {
  children: ReactNode;
  fallback?: ReactNode;
};

export function AzureAuthGuard({ children, fallback }: AzureAuthGuardProps) {
  const router = useRouter();
  const { loading, authenticated } = useAuthContext();

  if (loading) {
    return fallback || <div>Loading...</div>;
  }

  if (!authenticated) {
    router.push(paths.auth.azure.signIn);
    return fallback || null;
  }

  return <>{children}</>;
}

// ----------------------------------------------------------------------

export function AzureGuestGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { loading, authenticated } = useAuthContext();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (authenticated) {
    router.push(paths.dashboard.root);
    return null;
  }

  return <>{children}</>;
}
