import type { Metadata } from 'next';

import { HomeView } from 'src/sections/home/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = {
  title: 'Droit AI: Enterprise AI-Powered Knowledge Retrieval',
  keywords: ['Droit AI', 'Enterprise RAG', 'Azure AI Search', 'Retrieval Augmented Generation', 'Enterprise AI', 'Azure OpenAI'],
  description:
    'Droit AI is an enterprise-grade RAG system powered by Azure AI Search and Azure OpenAI, providing accurate, verifiable answers with enterprise security',
  openGraph: {
    title: 'Droit AI: Enterprise AI-Powered Knowledge Retrieval',
    description: 'Droit AI is an enterprise-grade RAG system powered by Azure AI Search and Azure OpenAI, providing accurate, verifiable answers with enterprise security',
    type: 'website',
    url: 'https://droit.ai',
    siteName: 'Droit AI',
    images: [
      {
        url: 'https://droit.ai/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Droit AI: Enterprise AI-Powered Knowledge Retrieval',
      },
    ],
  },
  twitter: {
    title: 'Droit AI: Enterprise AI-Powered Knowledge Retrieval',
    description: 'Droit AI is an enterprise-grade RAG system powered by Azure AI Search and Azure OpenAI, providing accurate, verifiable answers with enterprise security',
    card: 'summary_large_image',
    images: [
      {
        url: 'https://droit.ai/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Droit AI: Enterprise AI-Powered Knowledge Retrieval',
      },
    ],
  },
};

export default function Page() {
  return <HomeView />;
}
