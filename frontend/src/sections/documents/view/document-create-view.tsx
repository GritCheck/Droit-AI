'use client';

import Box from '@mui/material/Box';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { Upload } from 'src/components/upload';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

// ----------------------------------------------------------------------

export function DocumentCreateView() {
  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Upload a new document"
        links={[
          { name: 'Dashboard', href: paths.dashboard.root },
          { name: 'Documents', href: paths.dashboard.fileManager },
          { name: 'Upload document' },
        ]}
        sx={{ mb: { xs: 3, md: 5 } }}
      />

      <Upload
        onUpload={() => console.log('Document upload functionality to be implemented')}
        helperText="Drag & drop your document here or click to browse"
        placeholder={
          <Box sx={{ textAlign: 'center', py: 3 }}>
            Upload documents for AI processing and vector indexing
          </Box>
        }
      />
    </DashboardContent>
  );
}
