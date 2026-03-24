'use client';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import Button from '@mui/material/Button';
import { useTheme } from '@mui/material/styles';

import { useDashboardData } from 'src/hooks/useDashboardData';

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

export function OverviewAppView() {
  const { data: dashboardData, loading, error } = useDashboardData();
  const theme = useTheme();

  // Show loading state
  if (loading) {
    return (
      <DashboardContent maxWidth="xl">
        <Box sx={{ p: 3, textAlign: 'center' }}>
          Loading dashboard...
        </Box>
      </DashboardContent>
    );
  }

  // Show error state
  if (error || !dashboardData) {
    return (
      <DashboardContent maxWidth="xl">
        <Box sx={{ p: 3, textAlign: 'center', color: 'error.main' }}>
          Error loading dashboard: {error || 'Unknown error'}
        </Box>
      </DashboardContent>
    );
  }

  return (
    <DashboardContent maxWidth="xl">
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          <AppWelcome
            title={dashboardData.welcome.title}
            description={dashboardData.welcome.description}
            img={<SeoIllustration hideBackground />}
            action={
              <Button variant="contained" color="primary" href={dashboardData.welcome.actionHref}>
                {dashboardData.welcome.actionText}
              </Button>
            }
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppFeatured list={_appFeatured} />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
              title={dashboardData.stats.groundedness.title}
              percent={dashboardData.stats.groundedness.percent}
              total={dashboardData.stats.groundedness.total}
              chart={{
                categories: dashboardData.stats.groundedness.categories,
                series: dashboardData.stats.groundedness.series,
              }}
            />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
              title={dashboardData.stats.indexing.title}
              percent={dashboardData.stats.indexing.percent}
              total={dashboardData.stats.indexing.total}
              chart={{
                colors: [theme.palette.info.main],
                categories: dashboardData.stats.indexing.categories,
                series: dashboardData.stats.indexing.series,
              }}
            />

        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
              title={dashboardData.stats.compliance.title}
              percent={dashboardData.stats.compliance.percent}
              total={dashboardData.stats.compliance.total}
              chart={{
                colors: [theme.palette.error.main],
                categories: dashboardData.stats.compliance.categories,
                series: dashboardData.stats.compliance.series,
              }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AppCurrentDownload
            title={dashboardData.charts.distribution.title}
            subheader={dashboardData.charts.distribution.subheader}
            chart={{
              series: dashboardData.charts.distribution.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 8 }}>
          <AppAreaInstalled
            title={dashboardData.charts.volume.title}
            subheader={dashboardData.charts.volume.subheader}
            chart={{
              categories: dashboardData.charts.volume.categories,
              series: dashboardData.charts.volume.series,
            }}/>
        </Grid>

        <Grid size={{ xs: 12, lg: 8 }}>
          <AppNewInvoice
            title={dashboardData.audit.title}
            tableData={_appInvoices}
            headCells={dashboardData.audit.headers}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AppTopRelated title={dashboardData.recent.title} list={dashboardData.recent.list} />
        </Grid>



        <Grid size={{ xs: 12, md: 12, lg: 12 }}>
          <Box sx={{ gap: 3, display: 'flex', flexDirection: 'row' }}>
            <AppWidget
              title={dashboardData.widgets.optimization.title}
              total={dashboardData.widgets.optimization.total}
              icon={dashboardData.widgets.optimization.icon}
              chart={{ series: dashboardData.widgets.optimization.series }}
            />

            <AppWidget
              title={dashboardData.widgets.azureTokens.title}
              total={dashboardData.widgets.azureTokens.total}
              icon={dashboardData.widgets.azureTokens.icon}
              chart={{
                series: dashboardData.widgets.azureTokens.series,
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
