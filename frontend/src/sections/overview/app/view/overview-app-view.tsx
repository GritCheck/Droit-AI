'use client';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import Button from '@mui/material/Button';
import { useTheme } from '@mui/material/styles';

import { _appFeatured, _appInvoices } from 'src/_mock';
import { DashboardContent } from 'src/layouts/dashboard';
import { SeoIllustration } from 'src/assets/illustrations';

import { svgColorClasses } from 'src/components/svg-color';

import { AppWidget } from '../app-widget';
import { AppWelcome } from '../app-welcome';
import { AppFeatured } from '../app-featured';
import { AppNewInvoice } from '../app-new-invoice';
import { AppTopRelated } from '../app-top-related';
import { AppAreaInstalled } from '../app-area-installed';
import { AppWidgetSummary } from '../app-widget-summary';
import { AppCurrentDownload } from '../app-current-download';

// ----------------------------------------------------------------------

// TODO: API INTEGRATION POINT
// Replace DROIT_DASHBOARD_DATA with a 'useDashboardData()' hook 
// fetching from Azure AI Search and SentinelRAG API.

const DROIT_DASHBOARD_DATA = {
  welcome: {
    title: "Welcome to Droit AI Workspace ⚖️",
    description: "Azure-governed intelligence for regulated industries.",
    actionText: "Explore Knowledge Base",
    actionHref: 'user/'
  },
  stats: {
    groundedness: {
      title: "Groundedness Score",
      percent: 2.6,
      total: 4.9,
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
      series: [15, 18, 12, 51, 68, 11, 39, 37]
    },
    indexing: {
      title: "Indexed Documents (ADLS)",
      percent: 0.2,
      total: 2448,
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
      series: [20, 41, 63, 33, 28, 35, 50, 46]
    },
    compliance: {
      title: "Compliance Violations",
      percent: -100,
      total: 0,
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
      series: [18, 19, 31, 8, 16, 37, 12, 33]
    }
  },
  charts: {
    distribution: {
      title: "Knowledge Source Distribution",
      subheader: "",
      series: [
        { label: 'Legal Contracts', value: 2448 },
        { label: 'Clinical SOPs', value: 1206 },
        { label: 'Technical Docs', value: 0 },
      ]
    },
    volume: {
      title: "Query Volume & Accuracy",
      subheader: "(+43%) grounded responses than last year",
      categories: [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ],
      series: [
        {
          name: 'Grounded',
          data: [{ name: 'Grounded', data: [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16] }]
        },
        {
          name: 'Safety-Filtered',
          data: [{ name: 'Safety-Filtered', data: [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16] }]
        }
      ]
    }
  },
  audit: {
    title: "Governance Audit Trail",
    headers: [
      { id: 'id', label: 'Request ID' },
      { id: 'category', label: 'User Group' },
      { id: 'price', label: 'Safety Score' },
      { id: 'status', label: 'Status' },
      { id: '' },
    ]
  },
  widgets: {
    optimization: {
      title: "Index Optimization",
      total: 48,
      icon: "solar:user-rounded-bold",
      series: 48
    },
    azureTokens: {
      title: "Azure Token Usage",
      total: 55566,
      icon: "fluent:mail-24-filled",
      series: 75
    }
  },
  recent: {
    title: "Recent Document Ingestions",
    list: []
  }
};

export function OverviewAppView() {

  const theme = useTheme();

  return (
    <DashboardContent maxWidth="xl">
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          <AppWelcome
            title={DROIT_DASHBOARD_DATA.welcome.title}
            description={DROIT_DASHBOARD_DATA.welcome.description}
            img={<SeoIllustration hideBackground />}
            action={
              <Button variant="contained" color="primary" href={DROIT_DASHBOARD_DATA.welcome.actionHref}>
                {DROIT_DASHBOARD_DATA.welcome.actionText}
              </Button>
            }
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppFeatured list={_appFeatured} />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
              title={DROIT_DASHBOARD_DATA.stats.groundedness.title}
              percent={DROIT_DASHBOARD_DATA.stats.groundedness.percent}
              total={DROIT_DASHBOARD_DATA.stats.groundedness.total}
              chart={{
                categories: DROIT_DASHBOARD_DATA.stats.groundedness.categories,
                series: DROIT_DASHBOARD_DATA.stats.groundedness.series,
              }}
            />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
              title={DROIT_DASHBOARD_DATA.stats.indexing.title}
              percent={DROIT_DASHBOARD_DATA.stats.indexing.percent}
              total={DROIT_DASHBOARD_DATA.stats.indexing.total}
              chart={{
                colors: [theme.palette.info.main],
                categories: DROIT_DASHBOARD_DATA.stats.indexing.categories,
                series: DROIT_DASHBOARD_DATA.stats.indexing.series,
              }}
            />

        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
              title={DROIT_DASHBOARD_DATA.stats.compliance.title}
              percent={DROIT_DASHBOARD_DATA.stats.compliance.percent}
              total={DROIT_DASHBOARD_DATA.stats.compliance.total}
              chart={{
                colors: [theme.palette.error.main],
                categories: DROIT_DASHBOARD_DATA.stats.compliance.categories,
                series: DROIT_DASHBOARD_DATA.stats.compliance.series,
              }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AppCurrentDownload
            title={DROIT_DASHBOARD_DATA.charts.distribution.title}
            subheader={DROIT_DASHBOARD_DATA.charts.distribution.subheader}
            chart={{
              series: DROIT_DASHBOARD_DATA.charts.distribution.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 8 }}>
          <AppAreaInstalled
            title={DROIT_DASHBOARD_DATA.charts.volume.title}
            subheader={DROIT_DASHBOARD_DATA.charts.volume.subheader}
            chart={{
              categories: DROIT_DASHBOARD_DATA.charts.volume.categories,
              series: DROIT_DASHBOARD_DATA.charts.volume.series,
            }}/>
        </Grid>

        <Grid size={{ xs: 12, lg: 8 }}>
          <AppNewInvoice
            title={DROIT_DASHBOARD_DATA.audit.title}
            tableData={_appInvoices}
            headCells={DROIT_DASHBOARD_DATA.audit.headers}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AppTopRelated title={DROIT_DASHBOARD_DATA.recent.title} list={DROIT_DASHBOARD_DATA.recent.list} />
        </Grid>



        <Grid size={{ xs: 12, md: 12, lg: 12 }}>
          <Box sx={{ gap: 3, display: 'flex', flexDirection: 'row' }}>
            <AppWidget
              title={DROIT_DASHBOARD_DATA.widgets.optimization.title}
              total={DROIT_DASHBOARD_DATA.widgets.optimization.total}
              icon={DROIT_DASHBOARD_DATA.widgets.optimization.icon}
              chart={{ series: DROIT_DASHBOARD_DATA.widgets.optimization.series }}
            />

            <AppWidget
              title={DROIT_DASHBOARD_DATA.widgets.azureTokens.title}
              total={DROIT_DASHBOARD_DATA.widgets.azureTokens.total}
              icon={DROIT_DASHBOARD_DATA.widgets.azureTokens.icon}
              chart={{
                series: DROIT_DASHBOARD_DATA.widgets.azureTokens.series,
                colors: [theme.vars.palette.info.light, theme.vars.palette.info.main],
              }}
              sx={{ bgcolor: 'info.dark', [`& .${svgColorClasses.root}`]: { color: 'info.light' } }}
            />
          </Box>
        </Grid>
      </Grid>
    </DashboardContent>
  );
}
