import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { DocumentCreateView } from 'src/sections/documents/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Create a new document | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <DocumentCreateView />;
}
