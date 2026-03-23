import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { KnowledgeBaseManager } from 'src/sections/documents/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Documents list | Dashboard - ${CONFIG.appName}` };

export default function Page() {
  return <KnowledgeBaseManager />;
}
