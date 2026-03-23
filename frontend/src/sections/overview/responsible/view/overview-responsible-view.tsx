'use client';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';

import { DashboardContent } from 'src/layouts/dashboard';
import { _bookings, _bookingNew, _bookingReview } from 'src/_mock';
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
  // AI Governance Dashboard Constants
  const totalAssertions = 12450;
  const safetyFiltered = 9876;
  const highConfidenceCitations = 8234;

  return (
    <DashboardContent maxWidth="xl">
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <ResWidgetSummary
            title="Total AI Assertions"
            percent={0}
            total={totalAssertions}
            icon={<BookingIllustration />}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <ResWidgetSummary
            title="Safety-Filtered Responses"
            percent={0}
            total={safetyFiltered}
            icon={<CheckInIllustration />}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <ResWidgetSummary
            title="High-Confidence Citations"
            percent={0}
            total={highConfidenceCitations}
            icon={<CheckoutIllustration />}
          />
        </Grid>

        <Grid container size={12}>
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
                  title="Query Groundedness Score"
                  total={89.2}
                  percent={2.6}
                  chart={{
                    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                    series: [{ data: [85, 87, 88, 89, 88, 90, 89, 91, 89.2] }],
                  }}
                />

                <ResBooked
                  title="Response Reliability"
                  data={[
                    { value: 85, status: 'Fully Grounded', quantity: 10582 },
                    { value: 12, status: 'Partially Cited', quantity: 1494 },
                    { value: 3, status: 'Requires Review', quantity: 374 },
                  ]}
                  sx={{ boxShadow: { md: 'none' } }}
                />
              </Box>

              <ResCheckInWidgets
                chart={{
                  series: [
                    { label: 'PII Redaction Success', percent: 94.2, total: 11732 },
                    { label: 'Jailbreak Attempts Blocked', percent: 87.8, total: 10932 },
                  ],
                }}
                sx={{ boxShadow: { md: 'none' } }}
              />
            </Box>

            <ResStatistics
              title="Model Performance Telemetry"
              chart={{
                series: [
                  {
                    name: 'Weekly',
                    categories: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
                    data: [
                      { name: 'Coherence Score', data: [92, 91, 93, 94, 93] },
                      { name: 'Relevance Score', data: [88, 89, 87, 90, 91] },
                    ],
                  },
                  {
                    name: 'Monthly',
                    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                    data: [
                      { name: 'Coherence Score', data: [90, 91, 92, 91, 93, 92, 94, 93, 92] },
                      { name: 'Relevance Score', data: [87, 88, 86, 89, 88, 90, 89, 91, 90] },
                    ],
                  },
                  {
                    name: 'Yearly',
                    categories: ['2018', '2019', '2020', '2021', '2022', '2023'],
                    data: [
                      { name: 'Coherence Score', data: [85, 87, 89, 91, 92, 93] },
                      { name: 'Relevance Score', data: [82, 84, 86, 88, 89, 90] },
                    ],
                  },
                ],
              }}
            />
          </Grid>

          <Grid size={{ xs: 12, md: 5, lg: 4 }}>
            <Box sx={{ gap: 3, display: 'flex', flexDirection: 'column' }}>
              <ResAvailable
                title="Content Moderation Distribution"
                chart={{
                  series: [
                    { label: 'Hate/Bias Blocked', value: 247 },
                    { label: 'Safe to Deploy', value: 12203 },
                  ],
                }}
              />

              <ResCustomerReviews
                title="System Feedback Audit"
                subheader="Internal Expert Review Tags"
                list={_bookingReview}
              />
            </Box>
          </Grid>
        </Grid>

        <Grid size={12}>
          <ResNewest
            title="Recent Flagged Interventions"
            subheader={`${_bookingNew.length} interventions`}
            list={_bookingNew}
          />
        </Grid>

        <Grid size={12}>
          <ResDetails
            title="Governance Audit Trail"
            tableData={_bookings}
            headCells={[
              { id: 'destination', label: 'Query Intent' },
              { id: 'customer', label: 'User Group' },
              { id: 'checkIn', label: 'Safety Score' },
              { id: 'checkOut', label: 'Audit Timestamp' },
              { id: 'status', label: 'Action Taken' },
              { id: '' },
            ]}
          />
        </Grid>
      </Grid>
    </DashboardContent>
  );
}
