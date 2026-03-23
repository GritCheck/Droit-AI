'use client';

import Grid from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';

import { CONFIG } from 'src/global-config';
import { DashboardContent } from 'src/layouts/dashboard';
import {
  _analyticTasks,
  _analyticPosts,
  _analyticTraffic,
  _analyticOrderTimeline,
} from 'src/_mock';

import { AnalyticsNews } from '../analytics-news';
import { AnalyticsTasks } from '../analytics-tasks';
import { AnalyticsCurrentVisits } from '../analytics-current-visits';
import { AnalyticsOrderTimeline } from '../analytics-order-timeline';
import { AnalyticsWebsiteVisits } from '../analytics-website-visits';
import { AnalyticsWidgetSummary } from '../analytics-widget-summary';
import { AnalyticsTrafficBySite } from '../analytics-traffic-by-site';
import { AnalyticsCurrentSubject } from '../analytics-current-subject';
import { AnalyticsConversionRates } from '../analytics-conversion-rates';

// ----------------------------------------------------------------------

// TODO: API INTEGRATION POINT - Replace ANALYTICS_DATA_MANIFEST with live telemetry from Azure Monitor and AI Search.

const ANALYTICS_DATA_MANIFEST = {
  summary: {
    queries: {
      title: "Total Semantic Queries",
      percent: 2.6,
      total: 714000,
      icon: `${CONFIG.assetsDir}/assets/icons/glass/ic-glass-search.svg`,
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
      series: [22, 8, 35, 50, 82, 84, 77, 12]
    },
    indexes: {
      title: "Active Vector Indexes",
      percent: -0.1,
      total: 1352831,
      color: "secondary" as const,
      icon: `${CONFIG.assetsDir}/assets/icons/glass/ic-glass-database.svg`,
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
      series: [56, 47, 40, 62, 73, 30, 23, 54]
    },
    storage: {
      title: "Knowledge Base Size (MB)",
      percent: 2.8,
      total: 1723315,
      color: "warning" as const,
      icon: `${CONFIG.assetsDir}/assets/icons/glass/ic-glass-storage.svg`,
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
      series: [40, 70, 50, 28, 70, 75, 7, 64]
    },
    latency: {
      title: "Avg. Retrieval Latency (ms)",
      percent: 3.6,
      total: 234,
      color: "error" as const,
      icon: `${CONFIG.assetsDir}/assets/icons/glass/ic-glass-timer.svg`,
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
      series: [56, 30, 23, 54, 47, 40, 62, 73]
    }
  },
  trends: {
    accuracy: {
      title: "Search Accuracy Trend",
      subheader: "(+12%) semantic relevance improvement",
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
      series: [
        { name: 'Hybrid Search', data: [43, 33, 22, 37, 67, 68, 37, 24, 55] },
        { name: 'Keyword Only', data: [51, 70, 47, 67, 40, 37, 24, 70, 24] }
      ]
    },
    distribution: {
      title: "Query Distribution by Department",
      series: [
        { label: 'Legal', value: 3500 },
        { label: 'HR', value: 2500 },
        { label: 'Operations', value: 1500 },
        { label: 'Finance', value: 500 }
      ]
    },
    retrievalFreq: {
      title: "Document Type Retrieval Frequency",
      subheader: "(+43%) than last year",
      categories: ['PDF SOPs', 'Excel Data', 'Legal Docs', 'Policy Memos'],
      series: [
        { name: '2022', data: [44, 55, 41, 64, 22] },
        { name: '2023', data: [53, 32, 33, 52, 13] }
      ]
    }
  },
  radar: {
    modelConfidence: {
      title: "Model Confidence Radar",
      categories: ['Groundedness', 'Coherence', 'Relevance', 'Safety', 'Fluency'],
      series: [
        { name: 'Series 1', data: [80, 50, 30, 40, 100, 20] },
        { name: 'Series 2', data: [20, 30, 40, 80, 20, 80] },
        { name: 'Series 3', data: [44, 76, 78, 13, 43, 10] }
      ]
    }
  },
  logs: {
    auditEvents: {
      title: "Recent System Audit Events"
    },
    pipelineStatus: {
      title: "Ingestion Pipeline Status"
    },
    serviceHealth: {
      title: "Azure Service Health"
    },
    tasks: {
      title: "Governance To-Do List"
    }
  }
};

export function OverviewAnalyticsView() {
  return (
    <DashboardContent maxWidth="xl">
      <Typography variant="h4" sx={{ mb: { xs: 3, md: 5 } }}>
        Search & Intelligence Insights �
      </Typography>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <AnalyticsWidgetSummary
            title={ANALYTICS_DATA_MANIFEST.summary.queries.title}
            percent={ANALYTICS_DATA_MANIFEST.summary.queries.percent}
            total={ANALYTICS_DATA_MANIFEST.summary.queries.total}
            icon={
              <img
                alt={ANALYTICS_DATA_MANIFEST.summary.queries.title}
                src={ANALYTICS_DATA_MANIFEST.summary.queries.icon}
              />
            }
            chart={{
              categories: ANALYTICS_DATA_MANIFEST.summary.queries.categories,
              series: ANALYTICS_DATA_MANIFEST.summary.queries.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <AnalyticsWidgetSummary
            title={ANALYTICS_DATA_MANIFEST.summary.indexes.title}
            percent={ANALYTICS_DATA_MANIFEST.summary.indexes.percent}
            total={ANALYTICS_DATA_MANIFEST.summary.indexes.total}
            color={ANALYTICS_DATA_MANIFEST.summary.indexes.color}
            icon={
              <img
                alt={ANALYTICS_DATA_MANIFEST.summary.indexes.title}
                src={ANALYTICS_DATA_MANIFEST.summary.indexes.icon}
              />
            }
            chart={{
              categories: ANALYTICS_DATA_MANIFEST.summary.indexes.categories,
              series: ANALYTICS_DATA_MANIFEST.summary.indexes.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <AnalyticsWidgetSummary
            title={ANALYTICS_DATA_MANIFEST.summary.storage.title}
            percent={ANALYTICS_DATA_MANIFEST.summary.storage.percent}
            total={ANALYTICS_DATA_MANIFEST.summary.storage.total}
            color={ANALYTICS_DATA_MANIFEST.summary.storage.color}
            icon={
              <img
                alt={ANALYTICS_DATA_MANIFEST.summary.storage.title}
                src={ANALYTICS_DATA_MANIFEST.summary.storage.icon}
              />
            }
            chart={{
              categories: ANALYTICS_DATA_MANIFEST.summary.storage.categories,
              series: ANALYTICS_DATA_MANIFEST.summary.storage.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <AnalyticsWidgetSummary
            title={ANALYTICS_DATA_MANIFEST.summary.latency.title}
            percent={ANALYTICS_DATA_MANIFEST.summary.latency.percent}
            total={ANALYTICS_DATA_MANIFEST.summary.latency.total}
            color={ANALYTICS_DATA_MANIFEST.summary.latency.color}
            icon={
              <img
                alt={ANALYTICS_DATA_MANIFEST.summary.latency.title}
                src={ANALYTICS_DATA_MANIFEST.summary.latency.icon}
              />
            }
            chart={{
              categories: ANALYTICS_DATA_MANIFEST.summary.latency.categories,
              series: ANALYTICS_DATA_MANIFEST.summary.latency.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AnalyticsCurrentVisits
            title={ANALYTICS_DATA_MANIFEST.trends.distribution.title}
            chart={{
              series: ANALYTICS_DATA_MANIFEST.trends.distribution.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 8 }}>
          <AnalyticsWebsiteVisits
            title={ANALYTICS_DATA_MANIFEST.trends.accuracy.title}
            subheader={ANALYTICS_DATA_MANIFEST.trends.accuracy.subheader}
            chart={{
              categories: ANALYTICS_DATA_MANIFEST.trends.accuracy.categories,
              series: ANALYTICS_DATA_MANIFEST.trends.accuracy.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 8 }}>
          <AnalyticsConversionRates
            title={ANALYTICS_DATA_MANIFEST.trends.retrievalFreq.title}
            subheader={ANALYTICS_DATA_MANIFEST.trends.retrievalFreq.subheader}
            chart={{
              categories: ANALYTICS_DATA_MANIFEST.trends.retrievalFreq.categories,
              series: ANALYTICS_DATA_MANIFEST.trends.retrievalFreq.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AnalyticsCurrentSubject
            title={ANALYTICS_DATA_MANIFEST.radar.modelConfidence.title}
            chart={{
              categories: ANALYTICS_DATA_MANIFEST.radar.modelConfidence.categories,
              series: ANALYTICS_DATA_MANIFEST.radar.modelConfidence.series,
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 8 }}>
          <AnalyticsNews title={ANALYTICS_DATA_MANIFEST.logs.auditEvents.title} list={_analyticPosts} />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AnalyticsOrderTimeline title={ANALYTICS_DATA_MANIFEST.logs.pipelineStatus.title} list={_analyticOrderTimeline} />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AnalyticsTrafficBySite title={ANALYTICS_DATA_MANIFEST.logs.serviceHealth.title} list={_analyticTraffic} />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 8 }}>
          <AnalyticsTasks title={ANALYTICS_DATA_MANIFEST.logs.tasks.title} list={_analyticTasks} />
        </Grid>
      </Grid>
    </DashboardContent>
  );
}
