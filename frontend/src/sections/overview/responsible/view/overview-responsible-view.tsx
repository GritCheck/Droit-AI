'use client';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';

import { useResponsibleData } from 'src/hooks/useResponsibleData';

import { DashboardContent } from 'src/layouts/dashboard';
import {
  BookingIllustration,
  CheckInIllustration,
  CheckoutIllustration,
} from 'src/assets/illustrations';

import { ResBooked } from '../res-booked';
import { ResNewest } from '../res-newest';
import { ResDetails } from '../res-details';
import { ResAvailable } from '../res-available';
import { ResStatistics } from '../res-statistics';
import { ResTotalIncomes } from '../res-total-incomes';
import { ResWidgetSummary } from '../res-widget-summary';
import { ResCheckInWidgets } from '../res-check-in-widgets';
import { ResCustomerReviews } from '../res-customer-reviews';



export function ResponsibleView() {
  const { data: responsibleData, loading, error } = useResponsibleData();

  // Show loading state
  if (loading) {
    return (
      <DashboardContent maxWidth="xl">
        <Box sx={{ p: 3, textAlign: 'center' }}>
          Loading responsible AI data...
        </Box>
      </DashboardContent>
    );
  }

  // Show error state
  if (error || !responsibleData) {
    return (
      <DashboardContent maxWidth="xl">
        <Box sx={{ p: 3, textAlign: 'center', color: 'error.main' }}>
          Error loading responsible AI data: {error || 'Unknown error'}
        </Box>
      </DashboardContent>
    );
  }

  return (
    <DashboardContent maxWidth="xl">
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <ResWidgetSummary
            title="Total AI Assertions"
            percent={0}
            total={responsibleData.summary.totalAssertions}
            icon={<BookingIllustration />}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <ResWidgetSummary
            title="Safety-Filtered Responses"
            percent={0}
            total={responsibleData.summary.safetyFiltered}
            icon={<CheckInIllustration />}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <ResWidgetSummary
            title="High-Confidence Citations"
            percent={0}
            total={responsibleData.summary.highConfidenceCitations}
            icon={<CheckoutIllustration />}
          />
        </Grid>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 7, lg: 8 }}>
            <Box
              sx={{
                mb: 3,
                p: { md: 1 },
                display: 'flex',
                gap: { xs: 3, md: 1 },
                borderRadius: { md: 2 },
                flexDirection: 'column',
                bgcolor: { md: 'background.neutral' },
              }}
            >
              <Box
                sx={{
                  p: { md: 1 },
                  display: 'grid',
                  gap: { xs: 3, md: 0 },
                  borderRadius: { md: 2 },
                  bgcolor: { md: 'background.paper' },
                  gridTemplateColumns: { xs: 'repeat(1, 1fr)', md: 'repeat(2, 1fr)' },
                }}
              >
                <ResTotalIncomes
                  title={responsibleData.groundedness.title}
                  total={responsibleData.groundedness.total}
                  percent={responsibleData.groundedness.percent}
                  chart={responsibleData.groundedness.chart}
                />

                <ResBooked
                  title={responsibleData.reliability.title}
                  data={responsibleData.reliability.data}
                  sx={{ boxShadow: { md: 'none' } }}
                />
              </Box>

              <ResCheckInWidgets
                chart={responsibleData.safetyChecks.chart}
                sx={{ boxShadow: { md: 'none' } }}
              />
            </Box>

            <ResStatistics
              title={responsibleData.performance.title}
              chart={responsibleData.performance.chart}
            />
          </Grid>

          <Grid size={{ xs: 12, md: 5, lg: 4 }}>
            <Box sx={{ gap: 3, display: 'flex', flexDirection: 'column' }}>
              <ResAvailable
                title={responsibleData.moderation.title}
                chart={responsibleData.moderation.chart}
              />

              <ResCustomerReviews
                title={responsibleData.feedback.title}
                subheader={responsibleData.feedback.subheader}
                list={responsibleData.feedback.list}
              />
            </Box>
          </Grid>
        </Grid>

        <Grid size={12}>
          <ResNewest
            title={responsibleData.interventions.title}
            subheader={`${responsibleData.interventions.list.length} interventions`}
            list={responsibleData.interventions.list}
          />
        </Grid>

        <Grid size={12}>
          <ResDetails
            title={responsibleData.audit.title}
            tableData={responsibleData.audit.tableData}
            headCells={responsibleData.audit.headers}
          />
        </Grid>
      </Grid>
    </DashboardContent>
  );
}
