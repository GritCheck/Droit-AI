'use client';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { DocumentNewEditForm } from '../document-new-edit-form';

// ----------------------------------------------------------------------

export function DocumentCreateView() {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Create a new document"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Documents', href: paths.dashboard.fileManager },
          { name: 'New document' },
        ]}
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <DocumentNewEditForm />
    </DashboardContent>
  );
}
