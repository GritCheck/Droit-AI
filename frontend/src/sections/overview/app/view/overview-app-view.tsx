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
            title="Contracts Audited"
            percent={100}
            // total={dashboardData.summary.total_contracts_audited}
            total={510}
            chart={{
              categories: [],
              series: [],
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
            title="Index Storage"
            percent={dashboardData.summary.audit_success_rate}
            total={(37.04/1600000)*100}
            chart={{
              colors: [theme.palette.success.main],
              categories: [],
              series: [],
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
            title="Groundedness Rate"
            percent={dashboardData.summary.groundedness_rate}
            total={100}
            chart={{
              colors: [theme.palette.info.main],
              categories: [],
              series: [],
            }}
          />
        </Grid>

        {/* --- Risk Alerts --- */}
        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
            title="High Risk Clauses"
            percent={100}
            total={dashboardData.risk_alerts.high_risk_clauses_detected}
            chart={{
              colors: [theme.palette.error.main],
              categories: [],
              series: [],
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
            title="Compliance Issues"
            percent={100}
            total={dashboardData.risk_alerts.compliance_issues}
            chart={{
              colors: [theme.palette.warning.main],
              categories: [],
              series: [],
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
            title="Critical Findings"
            percent={100}
            total={dashboardData.risk_alerts.critical_findings}
            chart={{
              colors: [theme.palette.error.dark],
              categories: [],
              series: [],
            }}
          />
        </Grid>

        {/* --- Performance Metrics --- */}
        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AppCurrentDownload
            title="Doc Distribution"
            chart={{
              series: [
                { label: 'Efficiency Score', value: dashboardData.performance_metrics.cost_efficiency_score },
                { label: 'Token Utilization', value: dashboardData.performance_metrics.token_utilization_rate },
              ],
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 8 }}>
          <AppAreaInstalled
            title="Daily Audit Trends"
            subheader="Contract audits over the last 7 days"
            chart={{
              categories: dashboardData.trend_analysis.daily_audits.map(d => d.date),
              series: [{
                name: 'Daily Audits',
                data: [{ name: 'Daily Audits', data: dashboardData.trend_analysis.daily_audits.map(d => d.count || 0) }],
              }],
            }}
          />
        </Grid>

        {/* --- Compliance Breakdown --- */}
        <Grid size={{ xs: 12, lg: 8 }}>
          <AppNewInvoice
            title="Compliance Breakdown"
            tableData={[
              { id: '1', category: 'Fully Compliant', price: dashboardData.compliance_breakdown.fully_compliant, status: 'success', invoiceNumber: 'FC-001' },
              { id: '2', category: 'Partially Compliant', price: dashboardData.compliance_breakdown.partially_compliant, status: 'warning', invoiceNumber: 'PC-001' },
              { id: '3', category: 'Non-Compliant', price: dashboardData.compliance_breakdown.non_compliant, status: 'error', invoiceNumber: 'NC-001' },
            ]}
            headCells={[
              { id: 'invoiceNumber', label: 'Category ID' },
              { id: 'category', label: 'Compliance Status' },
              { id: 'price', label: 'Count' },
              { id: 'status', label: 'Risk Level' },
              { id: '', label: '' },
            ]}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AppTopRelated 
            title="Groundedness Trend" 
            list={dashboardData.trend_analysis.groundedness_trend.slice(0, 5).map(item => ({
              id: item.date,
              date: item.date,
              score: item.score || 0,
              category: 'Performance',
              image: null,
              postedAt: item.date,
            }))} 
          />
        </Grid>

        {/* --- Bottom Widgets --- */}
        <Grid size={{ xs: 12 }}>
          <Box sx={{ gap: 3, display: 'flex', flexDirection: 'row' }}>
            <AppWidget
              title="Avg Response Time"
              total={Math.round(dashboardData.performance_metrics.avg_response_time_ms)}
              icon="solar:timer-bold"
              chart={{
                series: dashboardData.performance_metrics.avg_response_time_ms / 100,
                colors: [theme.palette.info.light],
              }}
            />

            <AppWidget
              title="Avg Cost per Audit"
              total={dashboardData.summary.avg_cost_per_audit_tokens}
              icon="fluent:money-24-filled"
              chart={{
                series: dashboardData.summary.avg_cost_per_audit_tokens / 2,
                colors: [theme.palette.warning.main],
              }}
              sx={{ bgcolor: 'warning.dark', [`& .${svgColorClasses.root}`]: { color: 'warning.light' } }}
            />
          </Box>
        </Grid>
      </Grid>
    </DashboardContent>
  );
}