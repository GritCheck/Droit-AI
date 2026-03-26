'use client';

import type { ReactNode} from 'react';

import { useState, useEffect, useContext, createContext } from 'react';

import { CONFIG } from 'src/global-config';

import type { AuthState, AuthContextValue } from '../types';

// ----------------------------------------------------------------------

type AzureAuthContextValue = AuthContextValue & {
  login: () => Promise<void>;
  logout: () => Promise<void>;
  getAccessToken: () => Promise<string | null>;
};

const AzureAuthContext = createContext<AzureAuthContextValue | undefined>(undefined);

// ----------------------------------------------------------------------

type AzureAuthProviderProps = {
  children: ReactNode;
};

export function AzureAuthProvider({ children }: AzureAuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
  });

  const checkUserSession = async (): Promise<void> => {
    try {
      setState({ user: null, loading: true });

      // Check if we have a stored token
      const token = localStorage.getItem('azure_access_token');
      if (!token) {
        setState({ user: null, loading: false });
        return;
      }

      // Validate token and get user info
      const response = await fetch(`${CONFIG.serverUrl}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setState({ user: userData, loading: false });
      } else {
        // Token invalid, clear it
        localStorage.removeItem('azure_access_token');
        setState({ user: null, loading: false });
      }
    } catch (error) {
      console.error('Session check failed:', error);
      setState({ user: null, loading: false });
    }
  };

  const login = async (): Promise<void> => {
    try {
      const { azure } = CONFIG;
      
      // Build Azure AD login URL
      const authUrl = new URL(`${azure.authority}/${azure.tenantId}/oauth2/v2.0/authorize`);
      
      authUrl.searchParams.set('client_id', azure.clientId);
      authUrl.searchParams.set('response_type', 'code');
      authUrl.searchParams.set('redirect_uri', azure.redirectUri);
      authUrl.searchParams.set('scope', azure.scopes.join(' '));
      authUrl.searchParams.set('response_mode', 'query');
      authUrl.searchParams.set('state', crypto.randomUUID());

      // Redirect to Azure AD for login
      window.location.href = authUrl.toString();
    } catch (error) {
      console.error('Login failed:', error);
      setState({ user: null, loading: false });
    }
  };

  const logout = async (): Promise<void> => {
    try {
      // Clear local storage
      localStorage.removeItem('azure_access_token');
      
      // Redirect to Azure AD logout
      const { azure } = CONFIG;
      const logoutUrl = new URL(`${azure.authority}/${azure.tenantId}/oauth2/v2.0/logout`);
      logoutUrl.searchParams.set('post_logout_redirect_uri', window.location.origin);
      
      window.location.href = logoutUrl.toString();
    } catch (error) {
      console.error('Logout failed:', error);
      // Force logout even if Azure logout fails
      setState({ user: null, loading: false });
    }
  };

  const getAccessToken = async (): Promise<string | null> => {
    try {
      const token = localStorage.getItem('azure_access_token');
      
      if (!token) {
        return null;
      }

      // Check if token needs refresh (simplified - in production, implement proper token refresh)
      const response = await fetch(`${CONFIG.serverUrl}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('azure_access_token', data.access_token);
        return data.access_token;
      } else {
        // Token refresh failed, clear it
        localStorage.removeItem('azure_access_token');
        return null;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      return null;
    }
  };

  useEffect(() => {
    checkUserSession();
  }, []);

  // Handle Azure AD callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const authState = urlParams.get('state');
    const sessionState = urlParams.get('session_state');

    if (code) {
      const handleAzureCallback = async () => {
        try {
          setState({ user: null, loading: true });

          // Exchange authorization code for tokens
          const response = await fetch(`${CONFIG.serverUrl}/api/v1/auth/callback`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              code,
              state: authState || '',
              session_state: sessionState || '',
              redirect_uri: CONFIG.azure.redirectUri,
            }),
          });

          if (response.ok) {
            const data = await response.json();
            localStorage.setItem('azure_access_token', data.access_token);
            
            // Set user data directly from response (avoid extra /me call)
            if (data.user) {
              setState({ user: data.user, loading: false });
            }
            
            // Clean up URL
            window.history.replaceState({}, document.title, window.location.pathname);
          } else {
            console.error('Token exchange failed');
            setState({ user: null, loading: false });
          }
        } catch (error) {
          console.error('Callback handling failed:', error);
          setState({ user: null, loading: false });
        }
      };

      handleAzureCallback();
    }
  }, []);

  const memoizedValue: AzureAuthContextValue = {
    ...state,
    authenticated: !!state.user,
    unauthenticated: !state.user,
    checkUserSession,
    login,
    logout,
    getAccessToken,
  };

  return (
    <AzureAuthContext.Provider value={memoizedValue}>
      {children}
    </AzureAuthContext.Provider>
  );
}

// ----------------------------------------------------------------------

export const useAzureAuth = (): AzureAuthContextValue => {
  const context = useContext(AzureAuthContext);

  if (!context) {
    throw new Error('useAzureAuth must be used within an AzureAuthProvider');
  }

  return context;
};

// ----------------------------------------------------------------------

export const AzureAuthGuard = ({ children }: { children: ReactNode }) => {
  const { loading, authenticated } = useAzureAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!authenticated) {
    return <div>Please sign in to continue.</div>;
  }

  return <>{children}</>;
};
