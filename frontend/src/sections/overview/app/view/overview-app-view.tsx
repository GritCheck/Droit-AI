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

export function OverviewAppView() {

  const theme = useTheme();

  return (
    <DashboardContent maxWidth="xl">
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          <AppWelcome
            title="Welcome to Droit AI Workspace ⚖️"
            description="Azure-governed intelligence for regulated industries."
            img={<SeoIllustration hideBackground />}
            action={
              <Button variant="contained" color="primary" href='user/'>
                Explore Knowledge Base
              </Button>
            }
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppFeatured list={_appFeatured} />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
              title="Groundedness Score"
              percent={2.6}
              total={4.9}
              chart={{
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [15, 18, 12, 51, 68, 11, 39, 37],
              }}
            />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
              title="Indexed Documents (ADLS)"
              percent={0.2}
              total={2448}
              chart={{
                colors: [theme.palette.info.main],
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [20, 41, 63, 33, 28, 35, 50, 46],
              }}
            />

        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <AppWidgetSummary
              title="Compliance Violations"
              percent={-100}
              total={0}
              chart={{
                colors: [theme.palette.error.main],
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                series: [18, 19, 31, 8, 16, 37, 12, 33],
              }}
            />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AppCurrentDownload
            title="Knowledge Source Distribution"
            subheader=""
            chart={{
              series: [
                { label: 'Legal Contracts', value: 2448 },
                { label: 'Clinical SOPs', value: 1206 },
                { label: 'Technical Docs', value: 0 },
              ],
            }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 8 }}>
          <AppAreaInstalled
            title="Query Volume & Accuracy"
            subheader="(+43%) grounded responses than last year"
            chart={{
              categories: [
                'Jan',
                'Feb',
                'Mar',
                'Apr',
                'May',
                'Jun',
                'Jul',
                'Aug',
                'Sep',
                'Oct',
                'Nov',
                'Dec',
              ],
              series: [
                {
                  name: 'Grounded',
                  data: [ { name: 'Grounded', data: [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16] }]
                },
                {
                  name: 'Safety-Filtered',
                  data: [{ name: 'Safety-Filtered', data: [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16] }]
                },
              ],
            }}/>
        </Grid>

        <Grid size={{ xs: 12, lg: 8 }}>
          <AppNewInvoice
            title="Governance Audit Trail"
            tableData={_appInvoices}
            headCells={[
              { id: 'id', label: 'Request ID' },
              { id: 'category', label: 'User Group' },
              { id: 'price', label: 'Safety Score' },
              { id: 'status', label: 'Status' },
              { id: '' },
            ]}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
          <AppTopRelated title="Recent Document Ingestions" list={[]} />
        </Grid>



        <Grid size={{ xs: 12, md: 12, lg: 12 }}>
          <Box sx={{ gap: 3, display: 'flex', flexDirection: 'row' }}>
            <AppWidget
              title="Index Optimization"
              total={48}
              icon="solar:user-rounded-bold"
              chart={{ series: 48 }}
            />

            <AppWidget
              title="Azure Token Usage"
              total={55566}
              icon="fluent:mail-24-filled"
              chart={{
                series: 75,
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
