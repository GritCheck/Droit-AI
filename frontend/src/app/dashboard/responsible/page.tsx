import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { ResponsibleView } from 'src/sections/overview/responsible/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Responsible AI | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <ResponsibleView />;
}
