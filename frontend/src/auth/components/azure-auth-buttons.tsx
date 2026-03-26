'use client';

import { Button } from '@mui/material';

import { Iconify } from 'src/components/iconify';

import { useSignIn } from '../hooks/azure-auth-hooks';

// ----------------------------------------------------------------------

export function AzureSignInButton() {
  const signIn = useSignIn();

  const handleSignIn = async () => {
    await signIn();
  };

  return (
    <Button
      fullWidth
      size="large"
      color="inherit"
      variant="outlined"
      onClick={handleSignIn}
      startIcon={<Iconify icon="eva:log-in-fill" />}
    >
      Sign in with Azure AD
    </Button>
  );
}

// ----------------------------------------------------------------------

export function AzureSignOutButton() {
  const signOut = useSignOut();

  const handleSignOut = async () => {
    await signOut();
  };

  return (
    <Button
      color="inherit"
      onClick={handleSignOut}
      startIcon={<Iconify icon="eva:log-out-fill" />}
    >
      Sign out
    </Button>
  );
}
