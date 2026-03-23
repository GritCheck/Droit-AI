'use client';

import { useState, useCallback } from 'react';
import { useBoolean } from 'minimal-shared/hooks';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';

import { paths } from 'src/routes/paths';

import { CONFIG } from 'src/global-config';
import { _files, _folders } from 'src/_mock';
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

// TODO: API INTEGRATION POINT - Replace INGESTION_DATA_MANIFEST with live data from Azure Blob Storage (ADLS Gen2) and AI Search Indexer status.

const INGESTION_DATA_MANIFEST = {
  summary: {
    adls: {
      title: "Azure Data Lake (ADLS)",
      value: 24000000000, // GB / 10
      total: 24000000000, // GB
      icon: `${CONFIG.assetsDir}/assets/icons/apps/ic-app-azure.svg`
    },
    docling: {
      title: "Local Ingest (Docling)",
      value: 4800000000, // GB / 5
      total: 24000000000, // GB
      icon: `${CONFIG.assetsDir}/assets/icons/apps/ic-app-docling.svg`
    },
    aiSearch: {
      title: "Azure AI Search Index",
      value: 12000000000, // GB / 2
      total: 24000000000, // GB
      icon: `${CONFIG.assetsDir}/assets/icons/apps/ic-app-search.svg`
    }
  },
  storage: {
    totalGB: 24000000000, // GB constant
    usedPercent: 76,
    categories: [
      {
        name: 'Legal Docs',
        usedStorage: 12000000000, // GB / 2
        filesCount: 223,
        icon: `${CONFIG.assetsDir}/assets/icons/files/ic-legal.svg`
      },
      {
        name: 'Clinical Data',
        usedStorage: 4800000000, // GB / 5
        filesCount: 223,
        icon: `${CONFIG.assetsDir}/assets/icons/files/ic-clinical.svg`
      },
      {
        name: 'Standard Operating Procedures (SOPs)',
        usedStorage: 4800000000, // GB / 5
        filesCount: 223,
        icon: `${CONFIG.assetsDir}/assets/icons/files/ic-sop.svg`
      },
      {
        name: 'Technical Specs',
        usedStorage: 2400000000, // GB / 10
        filesCount: 223,
        icon: `${CONFIG.assetsDir}/assets/icons/files/ic-tech.svg`
      }
    ]
  },
  activity: {
    chartSeries: [
      {
        name: 'Weekly',
        categories: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
        data: [
          { name: 'Successful Indexing', data: [20, 34, 48, 65, 37] },
          { name: 'In-Progress', data: [10, 34, 13, 26, 27] },
          { name: 'Safety Flagged', data: [5, 12, 6, 7, 8] },
          { name: 'Other', data: [5, 12, 6, 7, 8] }
        ]
      },
      {
        name: 'Monthly',
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
        data: [
          { name: 'Successful Indexing', data: [10, 34, 13, 56, 77, 88, 99, 77, 45, 12, 43, 34] },
          { name: 'In-Progress', data: [10, 34, 13, 56, 77, 88, 99, 77, 45, 12, 43, 34] },
          { name: 'Safety Flagged', data: [10, 34, 13, 56, 77, 88, 99, 77, 45, 12, 43, 34] },
          { name: 'Other', data: [10, 34, 13, 56, 77, 88, 99, 77, 45, 12, 43, 34] }
        ]
      },
      {
        name: 'Yearly',
        categories: ['2018', '2019', '2020', '2021', '2022', '2023'],
        data: [
          { name: 'Successful Indexing', data: [24, 34, 32, 56, 77, 48] },
          { name: 'In-Progress', data: [24, 34, 32, 56, 77, 48] },
          { name: 'Safety Flagged', data: [24, 34, 32, 56, 77, 48] },
          { name: 'Other', data: [24, 34, 32, 56, 77, 48] }
        ]
      }
    ]
  },
  folders: _folders,
  recentFiles: _files
};

// ----------------------------------------------------------------------

export function OverviewFileView() {
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

  const renderStorageOverview = () => (
    <FileStorageOverview
      total={INGESTION_DATA_MANIFEST.storage.totalGB}
      chart={{ series: INGESTION_DATA_MANIFEST.storage.usedPercent }}
      data={INGESTION_DATA_MANIFEST.storage.categories.map(category => ({
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
              title={INGESTION_DATA_MANIFEST.summary.adls.title}
              value={INGESTION_DATA_MANIFEST.summary.adls.value}
              total={INGESTION_DATA_MANIFEST.summary.adls.total}
              icon={INGESTION_DATA_MANIFEST.summary.adls.icon}
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FileWidget
              title={INGESTION_DATA_MANIFEST.summary.docling.title}
              value={INGESTION_DATA_MANIFEST.summary.docling.value}
              total={INGESTION_DATA_MANIFEST.summary.docling.total}
              icon={INGESTION_DATA_MANIFEST.summary.docling.icon}
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FileWidget
              title={INGESTION_DATA_MANIFEST.summary.aiSearch.title}
              value={INGESTION_DATA_MANIFEST.summary.aiSearch.value}
              total={INGESTION_DATA_MANIFEST.summary.aiSearch.total}
              icon={INGESTION_DATA_MANIFEST.summary.aiSearch.icon}
            />
          </Grid>

          <Grid size={{ xs: 12, md: 6, lg: 8 }}>
            <FileDataActivity
              title="Indexing Activity"
              chart={{
                series: INGESTION_DATA_MANIFEST.activity.chartSeries,
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
                  {INGESTION_DATA_MANIFEST.folders.map((folder) => (
                    <FileManagerFolderItem
                      key={folder.id}
                      folder={folder}
                      onDelete={() => console.info('DELETE', folder.id)}
                      sx={{
                        ...(INGESTION_DATA_MANIFEST.folders.length > 3 && {
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
                {INGESTION_DATA_MANIFEST.recentFiles.slice(0, 5).map((file) => (
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
