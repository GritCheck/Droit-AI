import type { NavSectionProps } from 'src/components/nav-section';

import { paths } from 'src/routes/paths';

import { CONFIG } from 'src/global-config';

import { SvgColor } from 'src/components/svg-color';

// ----------------------------------------------------------------------

const icon = (name: string) => (
  <SvgColor src={`${CONFIG.assetsDir}/assets/icons/navbar/${name}.svg`} />
);

const ICONS = {
  job: icon('ic-job'),
  blog: icon('ic-blog'),
  chat: icon('ic-chat'),
  mail: icon('ic-mail'),
  user: icon('ic-user'),
  file: icon('ic-file'),
  lock: icon('ic-lock'),
  tour: icon('ic-tour'),
  order: icon('ic-order'),
  label: icon('ic-label'),
  blank: icon('ic-blank'),
  kanban: icon('ic-kanban'),
  folder: icon('ic-folder'),
  course: icon('ic-course'),
  banking: icon('ic-banking'),
  booking: icon('ic-booking'),
  invoice: icon('ic-invoice'),
  product: icon('ic-product'),
  calendar: icon('ic-calendar'),
  disabled: icon('ic-disabled'),
  external: icon('ic-external'),
  menuItem: icon('ic-menu-item'),
  ecommerce: icon('ic-ecommerce'),
  analytics: icon('ic-analytics'),
  dashboard: icon('ic-dashboard'),
  parameter: icon('ic-parameter'),
};

// ----------------------------------------------------------------------

export const navData: NavSectionProps['data'] = [
  /**
   * Core Intelligence
   */
  {
    subheader: 'Intelligence',
    items: [
      { 
        title: 'Overview', 
        path: paths.dashboard.root, 
        icon: ICONS.dashboard,
        caption: 'System health & Azure status' 
      },
      { 
        title: 'Governed Chat', 
        path: paths.dashboard.chat, // Reuse Chat page for RAG
        icon: ICONS.chat,
        info: 'SECURE' 
      },
      { 
        title: 'Enterprise Search', 
        path: paths.dashboard.general.analytics, // Reuse Analytics layout for Hybrid Search
        icon: ICONS.analytics 
      },
    ],
  },
  /**
   * Data & Ingestion
   */
  {
    subheader: 'Knowledge Management',
    items: [
      {
        title: 'Ingestion Pipeline',
        path: paths.dashboard.general.file, // Reuse File Manager for uploads
        icon: ICONS.folder,
        children: [
          { title: 'Upload & Index', path: paths.dashboard.general.file },
          { title: 'ADLS Gen2 Storage', path: '#adls-link' },
          { title: 'Processing Logs', path: '#logs' },
        ],
      },
      {
        title: 'Document Library',
        path: paths.dashboard.documents.list, // Updated from package to documents
        icon: ICONS.file,
        children: [
          { title: 'All Documents', path: paths.dashboard.documents.list },
          { title: 'Security Groups', path: paths.dashboard.permission }, // Reuse Permission guard
        ],
      },
    ],
  },
  /**
   * Governance & Trust
   */
  {
    subheader: 'Governance',
    items: [
      {
        title: 'Responsible AI',
        path: paths.dashboard.general.banking, // Reuse Banking for "Financial/Compliance" feel
        icon: ICONS.lock,
        children: [
          { title: 'AI Studio Metrics', path: '#metrics' },
          { title: 'Content Safety', path: '#safety' },
          { title: 'Audit Trail', path: paths.dashboard.invoice.root }, // Reuse Invoices for Audit logs
        ],
      },
      {
        title: 'System Settings',
        path: paths.dashboard.settings,
        icon: ICONS.parameter,
      },
    ],
  },
];
