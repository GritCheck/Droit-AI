'use client';

import { useState } from 'react';

import { Box, Card, Stack, Container, Typography } from '@mui/material';

import { paths } from 'src/routes/paths';

import { Logo } from 'src/components/logo';
import { Iconify } from 'src/components/iconify';

import { useAuthUser } from 'src/auth/hooks/azure-auth-hooks';
import { AzureSignInButton } from 'src/auth/components/azure-auth-buttons';

// ----------------------------------------------------------------------

export default function AzureSignInView() {
  const { loading } = useAuthUser();
  const [error, setError] = useState<string>('');

  const handleError = (message: string) => {
    setError(message);
    setTimeout(() => setError(''), 5000);
  };

  return (
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}
      >
        <Container maxWidth="sm">
          <Card
            sx={{
              p: 5,
              boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
              borderRadius: 2,
            }}
          >
            <Stack spacing={4} alignItems="center">
              <Logo sx={{ width: 64, height: 64 }} />

              <Stack spacing={1} alignItems="center" textAlign="center">
                <Typography variant="h4">Sign in to Droit AI</Typography>
                <Typography variant="body2" color="text.secondary">
                  Azure-governed intelligence for regulated industries
                </Typography>
              </Stack>

              {error && (
                <Box
                  sx={{
                    p: 2,
                    bgcolor: 'error.light',
                    color: 'error.contrastText',
                    borderRadius: 1,
                    textAlign: 'center',
                  }}
                >
                  <Typography variant="body2">{error}</Typography>
                </Box>
              )}

              <Stack spacing={2} width="100%">
                <AzureSignInButton />

                <Typography variant="caption" textAlign="center" color="text.secondary">
                  By signing in, you agree to our Terms of Service and Privacy Policy
                </Typography>
              </Stack>

              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  color: 'text.secondary',
                }}
              >
                <Iconify icon="eva:shield-fill" width={16} />
                <Typography variant="caption">
                  Secure authentication via Azure Active Directory
                </Typography>
              </Box>
            </Stack>
          </Card>
        </Container>
      </Box>
  );
}

// ----------------------------------------------------------------------

// Add the path to the auth routes
export const authPaths = {
  signIn: paths.auth.azure.signIn,
  signUp: paths.auth.azure.signUp,
  resetPassword: paths.auth.azure.resetPassword,
  verify: paths.auth.azure.verify,
};
