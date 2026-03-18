import type { Metadata } from 'next';

import { HomeView } from 'src/sections/home/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = {
  title: 'SentinelRAG: Enterprise AI-Powered Knowledge Retrieval',
  keywords: ['SentinelRAG', 'Enterprise RAG', 'Azure AI Search', 'Retrieval Augmented Generation', 'Enterprise AI', 'Azure OpenAI'],
  description:
    'SentinelRAG is an enterprise-grade RAG system powered by Azure AI Search and Azure OpenAI, providing accurate, verifiable answers with enterprise security',
  openGraph: {
    title: 'SentinelRAG: Enterprise AI-Powered Knowledge Retrieval',
    description: 'SentinelRAG is an enterprise-grade RAG system powered by Azure AI Search and Azure OpenAI, providing accurate, verifiable answers with enterprise security',
    type: 'website',
    url: 'https://sentinelrag.cc',
    siteName: 'SentinelRAG',
    images: [
      {
        url: 'https://sentinelrag.cc/og-image.png',
        width: 1200,
        height: 630,
        alt: 'SentinelRAG: Enterprise AI-Powered Knowledge Retrieval',
      },
    ],
  },
  twitter: {
    title: 'SentinelRAG: Enterprise AI-Powered Knowledge Retrieval',
    description: 'SentinelRAG is an enterprise-grade RAG system powered by Azure AI Search and Azure OpenAI, providing accurate, verifiable answers with enterprise security',
    card: 'summary_large_image',
    images: [
      {
        url: 'https://sentinelrag.cc/og-image.png',
        width: 1200,
        height: 630,
        alt: 'SentinelRAG: Enterprise AI-Powered Knowledge Retrieval',
      },
    ],
  },
};

export default function Page() {
  return <HomeView />;
}
