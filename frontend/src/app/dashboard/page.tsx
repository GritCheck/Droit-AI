import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { OverviewAppView } from 'src/sections/overview/app/view';

import { AzureAuthGuard } from 'src/auth/guard/azure-auth-guard';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return (
    <AzureAuthGuard>
      <OverviewAppView />
    </AzureAuthGuard>
  );
}
