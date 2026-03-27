import { paths } from 'src/routes/paths';

import packageJson from '../package.json';

// ----------------------------------------------------------------------

export type ConfigValue = {
  appName: string;
  appVersion: string;
  serverUrl: string;
  assetsDir: string;
  isStaticExport: boolean;
  auth: {
    method: 'azure';
    skip: boolean;
    redirectPath: string;
  };
  mapboxApiKey: string;
  
  azure: {
    clientId: string;
    tenantId: string;
    authority: string;
    redirectUri: string;
    scopes: string[];
  };
};

// ----------------------------------------------------------------------

export const CONFIG: ConfigValue = {
  appName: 'Droit AI',
  appVersion: packageJson.version,
  serverUrl: process.env.NEXT_PUBLIC_SERVER_URL ?? '',
  assetsDir: process.env.NEXT_PUBLIC_ASSETS_DIR ?? '',
  isStaticExport: JSON.parse(`${process.env.BUILD_STATIC_EXPORT}`),
  /**
   * Auth
   * @method jwt azure
   */
  auth: {
    method: 'azure',
    skip: false,
    redirectPath: paths.dashboard.root,
  },
  /**
   * Mapbox
   */
  mapboxApiKey: process.env.NEXT_PUBLIC_MAPBOX_API_KEY ?? '',
  /**
   * Azure AD
   */
  azure: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID ?? '',
    tenantId: process.env.NEXT_PUBLIC_AZURE_TENANT_ID ?? '',
    authority: process.env.NEXT_PUBLIC_AZURE_AUTHORITY ?? 'https://login.microsoftonline.com',
    redirectUri: process.env.NEXT_PUBLIC_AZURE_REDIRECT_URI ?? (typeof window !== 'undefined' ? `${window.location.origin}/auth/callback` : ''),
    scopes: [
      process.env.NEXT_PUBLIC_AZURE_API_SCOPE ?? 'api://backend/access_as_user',
      'openid',
      'profile',
      'email'
    ],
  },
};
