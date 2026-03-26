'use client';

import { useState, useEffect } from 'react';

import { Box, Typography, CircularProgress } from '@mui/material';

import { paths } from 'src/routes/paths';
import { useRouter, useSearchParams } from 'src/routes/hooks';

import { CONFIG } from 'src/global-config';

// ----------------------------------------------------------------------

export default function AzureCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const handleAzureCallback = async () => {
      try {
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const sessionState = searchParams.get('session_state');

        if (!code || !state) {
          throw new Error('Missing required OAuth parameters');
        }

        setStatus('processing');

        // Exchange authorization code for tokens
        const response = await fetch(`${CONFIG.serverUrl}/api/v1/auth/callback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            code,
            state,
            session_state: sessionState,
            redirect_uri: CONFIG.azure.redirectUri,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Store the access token
        if (data.access_token) {
          localStorage.setItem('azure_access_token', data.access_token);
        }

        // Store user info if available
        if (data.user) {
          localStorage.setItem('azure_user', JSON.stringify(data.user));
        }

        setStatus('success');

        // Get the return URL from state or default to dashboard
        const returnUrl = searchParams.get('returnTo') || paths.dashboard.root;
        
        // Redirect back to the originally requested page
        setTimeout(() => {
          router.push(returnUrl);
        }, 1000);

      } catch (err) {
        console.error('Azure callback error:', err);
        setError(err instanceof Error ? err.message : 'Authentication failed');
        setStatus('error');
      }
    };

    handleAzureCallback();
  }, [searchParams, router]);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Box
        sx={{
          p: 4,
          bgcolor: 'background.paper',
          borderRadius: 2,
          boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
          textAlign: 'center',
          minWidth: 300,
        }}
      >
        {status === 'processing' && (
          <>
            <CircularProgress size={48} sx={{ mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Signing you in...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Please wait while we authenticate with Azure AD
            </Typography>
          </>
        )}

        {status === 'success' && (
          <>
            <Typography variant="h6" color="success.main" gutterBottom>
              Authentication Successful!
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Redirecting you to the dashboard...
            </Typography>
          </>
        )}

        {status === 'error' && (
          <>
            <Typography variant="h6" color="error.main" gutterBottom>
              Authentication Failed
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {error}
            </Typography>
            <Typography
              variant="body2"
              component="a"
              href={paths.auth.azure.signIn}
              sx={{ 
                color: 'primary.main',
                textDecoration: 'underline',
                cursor: 'pointer'
              }}
            >
              Try again
            </Typography>
          </>
        )}
      </Box>
    </Box>
  );
}
