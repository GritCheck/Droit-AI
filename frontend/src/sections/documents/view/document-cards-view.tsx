'use client';

import Button from '@mui/material/Button';

import { paths } from 'src/routes/paths';
import { RouterLink } from 'src/routes/components';

import { _documents } from 'src/_mock/_documents';
import { DashboardContent } from 'src/layouts/dashboard';

import { Iconify } from 'src/components/iconify';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { DocumentCardList } from '../document-card-list';

// ----------------------------------------------------------------------

export function DocumentCardsView() {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Document cards"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Documents', href: paths.dashboard.fileManager },
          { name: 'Cards' },
        ]}
        action={
          <Button
            component={RouterLink}
            href={paths.dashboard.documents.new}
            variant="contained"
            startIcon={<Iconify icon="mingcute:add-line" />}
          >
            New document
          </Button>
        }
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <DocumentCardList documents={_documents} />
    </DashboardContent>
  );
}
