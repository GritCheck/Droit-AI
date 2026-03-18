import type { Metadata } from 'next';

import { HomeView } from 'src/sections/home/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = {
  title: 'AzubiISP: ISP Billing System',
  keywords: ['AzubiISP', 'ISP Billing System', 'ISP Billing System UI', 'ISP Billing System UI Kit', 'ISP Billing System UI Kit UI'],
  description:
    'AzubiISP is a billing system for ISPs, built on the newest version of Material-UI ©, ready to be customized to your style',
  openGraph: {
    title: 'AzubiISP: ISP Billing System',
    description: 'AzubiISP is a billing system for ISPs, built on the newest version of Material-UI ©, ready to be customized to your style',
    type: 'website',
    url: 'https://azubiisp.com',
    siteName: 'AzubiISP',
    images: [
      {
        url: 'https://azubiisp.com/og-image.png',
        width: 1200,
        height: 630,
        alt: 'AzubiISP: ISP Billing System',
      },
    ],
  },
  twitter: {
    title: 'AzubiISP: ISP Billing System',
    description: 'AzubiISP is a billing system for ISPs, built on the newest version of Material-UI ©, ready to be customized to your style',
    card: 'summary_large_image',
    images: [
      {
        url: 'https://azubiisp.com/og-image.png',
        width: 1200,
        height: 630,
        alt: 'AzubiISP: ISP Billing System',
      },
    ],
  },
};

export default function Page() {
  return <HomeView />;
}
