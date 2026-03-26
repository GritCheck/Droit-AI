'use client';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import Button from '@mui/material/Button';
import { useTheme } from '@mui/material/styles';

import { useDashboardData } from 'src/hooks/useDashboardData';

import { _appFeatured } from 'src/_mock';
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

  if (loading) {
    return (
      <DashboardContent maxWidth="xl">
        <Box sx={{ p: 3, textAlign: 'center' }}>Loading dashboard...</Box>
      </DashboardContent>
    );
  }

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
            title="Welcome to Droit AI Workspace ⚖️"
            description="Azure-governed intelligence for regulated industries."
            img={<SeoIllustration hideBackground />}
            action={
              <Button variant="contained" color="primary" href="/user">
                Explore Knowledge Base
              </Button>
            }
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppFeatured list={_appFeatured} />
        </Grid>

        {/* --- Summary Stats --- */}
        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
            title="Uptime"
            percent={dashboardData.stats.uptime?.percent || 0}
            total={dashboardData.stats.uptime?.total || 100}
            chart={{
              categories: dashboardData.stats.uptime?.categories || [],
              series: dashboardData.stats.uptime?.series || [],
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
            title="Latency"
            percent={dashboardData.stats.latency?.percent || 0}
            total={dashboardData.stats.latency?.total || 1000}
            chart={{
              colors: [theme.palette.warning.main],
              categories: dashboardData.stats.latency?.categories || [],
              series: dashboardData.stats.latency?.series || [],
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
            title="Compliance"
            percent={dashboardData.stats.compliance?.percent || 0}
            total={dashboardData.stats.compliance?.total || 100}
            chart={{
              colors: [theme.palette.success.main],
              categories: dashboardData.stats.compliance?.categories || [],
              series: dashboardData.stats.compliance?.series || [],
            }}
          />
        </Grid>

        {/* --- Charts --- */}
        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AppCurrentDownload
            title="Resource Distribution"
            chart={{
              // API provides { label, value }, which matches AppCurrentDownload
              series: dashboardData.charts.distribution.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 8 }}>
          <AppAreaInstalled
            title="Query Volume"
            subheader="System performance over time"
            chart={{
              categories: dashboardData.charts.volume.categories,
              // Map VolumeSeries[] to the nested structure Apex expects
              series: dashboardData.charts.volume.series.map((s) => ({
                name: s.name,
                data: [{ name: s.name, data: s.data.map(d => typeof d === 'number' ? d : d.value) }],
              })),
            }}
          />
        </Grid>

        {/* --- Audit Table --- */}
        <Grid size={{ xs: 12, lg: 8 }}>
          <AppNewInvoice
            title="Governance Audit Trail"
            tableData={dashboardData.audit.rows?.map((row: any) => ({
              id: row.id,
              category: row.category,
              price: row.score || 0,
              status: row.status,
              invoiceNumber: row.id,
            })) || []}
            headCells={[
              { id: 'id', label: 'Request ID' },
              { id: 'category', label: 'User Group' },
              { id: 'price', label: 'Safety Score' },
              { id: 'status', label: 'Status' },
              { id: '', label: '' },
            ]}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AppTopRelated title="Recent Documents" list={dashboardData.recent.list} />
        </Grid>

        {/* --- Bottom Widgets --- */}
        <Grid size={{ xs: 12 }}>
          <Box sx={{ gap: 3, display: 'flex', flexDirection: 'row' }}>
            <AppWidget
              title="Index Optimization"
              total={dashboardData.widgets.indexing?.total || 0}
              icon="solar:user-rounded-bold"
              chart={{
                // Ensure series is a single number, not an array
                series: Array.isArray(dashboardData.widgets.indexing?.series) 
                   ? dashboardData.widgets.indexing.series[0] 
                   : dashboardData.widgets.indexing?.series || 0,
                colors: [theme.palette.info.light], // Colors must be an array
              }}
            />

            <AppWidget
              title="Azure Tokens"
              total={dashboardData.widgets.azureTokens?.total || 0}
              icon="fluent:mail-24-filled"
              chart={{
                series: Array.isArray(dashboardData.widgets.azureTokens?.series)
                   ? dashboardData.widgets.azureTokens.series[0]
                   : dashboardData.widgets.azureTokens?.series || 0,
                colors: [theme.palette.info.main],
              }}
              sx={{ bgcolor: 'info.dark', [`& .${svgColorClasses.root}`]: { color: 'info.light' } }}
            />
          </Box>
        </Grid>
      </Grid>
    </DashboardContent>
  );
}