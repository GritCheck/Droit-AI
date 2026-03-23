// ----------------------------------------------------------------------
// Document Types for Droit AI Knowledge Base
// ----------------------------------------------------------------------

export interface IDocumentItem {
  id: string;
  name: string;
  type: string;
  data_limit: string; // Chunk Size in tokens
  rate_limit: string; // Vector Dimensions
  time_limit: string; // Last Synced
  session_timeout: number;
  idle_timeout: number;
  price: number; // Security Level (RLS)
  status: string; // 'indexed' | 'processing' | 'failed' | 'flagged' - accepting string for flexibility
  validity_period: string;
  features: string;
  subscribers: number;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface IDocumentCard {
  id: string;
  name: string;
  status: string;
  subscribers: number;
  data_limit: string;
  rate_limit: string;
}

export interface IDocumentTableFilters {
  name: string;
  type: string[];
  status: string;
}

// ----------------------------------------------------------------------
// Document Quick Edit Schema
// ----------------------------------------------------------------------

export interface IDocumentQuickEditSchemaType {
  name: string;
  type: string;
  data_limit: string;
  time_limit: string;
  rate_limit: string;
  session_timeout: number;
  idle_timeout: number;
  price: number;
  status: string;
  validity_period: string;
  features: string;
  subscribers: number;
  description: string;
}
