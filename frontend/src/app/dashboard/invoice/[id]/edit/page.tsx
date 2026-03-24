import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';
import { _invoices } from 'src/_mock/_invoice';

import { InvoiceEditView } from 'src/sections/invoice/view';

type Props = {
  params: Promise<{ id: string }>;
};

// Metadata must now await params
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;

  return {
    title: `Invoice ${id} Edit | Dashboard - ${CONFIG.appName}`,
  };
}

export default async function Page({ params }: Props) {
  // NEXT.JS 16 FIX: Must await params before destructuring
  const { id } = await params;

  const currentInvoice = _invoices.find((invoice) => invoice.id === id);

  return <InvoiceEditView invoice={currentInvoice} />;
}
export async function generateStaticParams() {
  if (CONFIG.isStaticExport) {
    return _invoices.map((invoice) => ({ id: invoice.id }));
  }
  return [];
}
