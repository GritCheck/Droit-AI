'use client';

import type { IDocumentItem } from 'src/types/document';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { DocumentNewEditForm } from '../document-new-edit-form';

// ----------------------------------------------------------------------

type Props = {
  package?: IDocumentItem;
};

export function PackageEditView({ package: currentPackage }: Props) {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Edit"
        backHref={paths.dashboard.documents.list}
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Documents', href: paths.dashboard.fileManager },
          { name: currentPackage?.name },
        ]}
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <DocumentNewEditForm currentDocument={currentPackage} />
    </DashboardContent>
  );
}
