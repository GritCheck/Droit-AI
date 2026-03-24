'use client';

import { useState, useCallback } from 'react';
import { useBoolean } from 'minimal-shared/hooks';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';

import { paths } from 'src/routes/paths';

import { useIngestionData } from 'src/hooks/useIngestionData';

import { DashboardContent } from 'src/layouts/dashboard';

import { Iconify } from 'src/components/iconify';
import { UploadBox } from 'src/components/upload';
import { Scrollbar } from 'src/components/scrollbar';

import { FileWidget } from '../../../file-manager/file-widget';
import { FileUpgrade } from '../../../file-manager/file-upgrade';
import { FileRecentItem } from '../../../file-manager/file-recent-item';
import { FileDataActivity } from '../../../file-manager/file-data-activity';
import { FileManagerPanel } from '../../../file-manager/file-manager-panel';
import { FileStorageOverview } from '../../../file-manager/file-storage-overview';
import { FileManagerFolderItem } from '../../../file-manager/file-manager-folder-item';
import { FileManagerNewFolderDialog } from '../../../file-manager/file-manager-new-folder-dialog';

// ----------------------------------------------------------------------

export function OverviewFileView() {
  const { data: ingestionData, loading, error } = useIngestionData();
  const [folderName, setFolderName] = useState('');
  const [files, setFiles] = useState<(File | string)[]>([]);

  const newFilesDialog = useBoolean();
  const newFolderDialog = useBoolean();

  const handleChangeFolderName = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setFolderName(event.target.value);
  }, []);

  const handleCreateNewFolder = useCallback(() => {
    newFolderDialog.onFalse();
    setFolderName('');
    console.info('CREATE NEW DOMAIN');
  }, [newFolderDialog]);

  const handleDrop = useCallback(
    (acceptedFiles: File[]) => {
      setFiles([...files, ...acceptedFiles]);
    },
    [files]
  );

  // Show loading state
  if (loading) {
    return (
      <DashboardContent maxWidth="xl">
        <Box sx={{ p: 3, textAlign: 'center' }}>
          Loading ingestion data...
        </Box>
      </DashboardContent>
    );
  }

  // Show error state
  if (error || !ingestionData) {
    return (
      <DashboardContent maxWidth="xl">
        <Box sx={{ p: 3, textAlign: 'center', color: 'error.main' }}>
          Error loading ingestion data: {error || 'Unknown error'}
        </Box>
      </DashboardContent>
    );
  }

  const renderStorageOverview = () => (
    <FileStorageOverview
      total={ingestionData.storage.totalGB}
      chart={{ series: ingestionData.storage.usedPercent }}
      data={ingestionData.storage.categories.map(category => ({
        ...category,
        icon: <Box component="img" src={category.icon} />
      }))}
    />
  );

  const renderNewFilesDialog = () => (
    <FileManagerNewFolderDialog open={newFilesDialog.value} onClose={newFilesDialog.onFalse} />
  );

  const renderNewFolderDialog = () => (
    <FileManagerNewFolderDialog
      open={newFolderDialog.value}
      onClose={newFolderDialog.onFalse}
      title="Domain Configuration"
      folderName={folderName}
      onChangeFolderName={handleChangeFolderName}
      onCreate={handleCreateNewFolder}
    />
  );

  return (
    <>
      <DashboardContent maxWidth="xl">
        <Typography variant="h4" sx={{ mb: { xs: 3, md: 5 } }}>
          Knowledge Ingestion Pipeline 📥
        </Typography>
        
        <Grid container spacing={3}>
          <Grid sx={{ display: { xs: 'block', sm: 'none' } }} size={12}>
            {renderStorageOverview()}
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FileWidget
              title={ingestionData.summary.adls.title}
              value={ingestionData.summary.adls.value}
              total={ingestionData.summary.adls.total}
              icon={ingestionData.summary.adls.icon}
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FileWidget
              title={ingestionData.summary.docling.title}
              value={ingestionData.summary.docling.value}
              total={ingestionData.summary.docling.total}
              icon={ingestionData.summary.docling.icon}
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FileWidget
              title={ingestionData.summary.aiSearch.title}
              value={ingestionData.summary.aiSearch.value}
              total={ingestionData.summary.aiSearch.total}
              icon={ingestionData.summary.aiSearch.icon}
            />
          </Grid>

          <Grid size={{ xs: 12, md: 6, lg: 8 }}>
            <FileDataActivity
              title="Indexing Activity"
              chart={{
                series: ingestionData.activity.chartSeries,
              }}
            />

            <Box sx={{ mt: 5 }}>
              <FileManagerPanel
                title="Knowledge Domains"
                link={paths.dashboard.documents.list}
                onOpen={newFolderDialog.onTrue}
              />

              <Scrollbar sx={{ mb: 3, minHeight: 186 }}>
                <Box sx={{ gap: 3, display: 'flex' }}>
                  {ingestionData.folders.map((folder) => (
                    <FileManagerFolderItem
                      key={folder.id}
                      folder={folder}
                      onDelete={() => console.info('DELETE', folder.id)}
                      sx={{
                        ...(ingestionData.folders.length > 3 && {
                          width: 240,
                          flexShrink: 0,
                        }),
                      }}
                    />
                  ))}
                </Box>
              </Scrollbar>

              <FileManagerPanel
                title="Recently Indexed Knowledge"
                link={paths.dashboard.documents.list}
                onOpen={newFilesDialog.onTrue}
              />

              <Box sx={{ gap: 2, display: 'flex', flexDirection: 'column' }}>
                {ingestionData.recentFiles.slice(0, 5).map((file) => (
                  <FileRecentItem
                    key={file.id}
                    file={file}
                    onDelete={() => console.info('DELETE', file.id)}
                  />
                ))}
              </Box>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, md: 6, lg: 4 }}>
            <Box sx={{ gap: 3, display: 'flex', flexDirection: 'column' }}>
              <UploadBox
                onDrop={handleDrop}
                placeholder={
                  <Box
                    sx={{
                      gap: 0.5,
                      display: 'flex',
                      alignItems: 'center',
                      color: 'text.secondary',
                    }}
                  >
                    <Iconify icon="solar:cloud-upload-bold" width={24} />
                    <Typography variant="body2">
                      Drop documents here for Azure-governed indexing (PDF, DOCX, XLSX)
                    </Typography>
                  </Box>
                }
                sx={{
                  py: 2.5,
                  width: 'auto',
                  height: 'auto',
                  borderRadius: 1.5,
                }}
              />

              <Box sx={{ display: { xs: 'none', sm: 'block' } }}>{renderStorageOverview()}</Box>

              <FileUpgrade />
            </Box>
          </Grid>
        </Grid>
      </DashboardContent>

      {renderNewFilesDialog()}
      {renderNewFolderDialog()}
    </>
  );
}
