'use client';

import { useState, useCallback } from 'react';
import { useBoolean } from 'minimal-shared/hooks';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { Iconify } from 'src/components/iconify';
import { UploadBox } from 'src/components/upload';
import { Scrollbar } from 'src/components/scrollbar';

import { FileWidget } from '../../../file-manager/file-widget';
import { FileRecentItem } from '../../../file-manager/file-recent-item';
import { FileDataActivity } from '../../../file-manager/file-data-activity';
import { FileManagerPanel } from '../../../file-manager/file-manager-panel';
import { FileStorageOverview } from '../../../file-manager/file-storage-overview';
import { FileManagerFolderItem } from '../../../file-manager/file-manager-folder-item';
import { FileManagerNewFolderDialog } from '../../../file-manager/file-manager-new-folder-dialog';

// ----------------------------------------------------------------------

// Helper function to convert size strings to bytes
const parseSizeToBytes = (size: string | number): number => {
  if (typeof size === 'number') {
    return size * 1024 * 1024; // Assume MB if number
  }
  
  if (typeof size === 'string') {
    const match = size.match(/^([\d.]+)(KB|MB|GB)?$/i);
    if (!match) return 0;
    
    const value = parseFloat(match[1]);
    const unit = (match[2] || 'MB').toUpperCase();
    
    switch (unit) {
      case 'KB': return value * 1024;
      case 'MB': return value * 1024 * 1024;
      case 'GB': return value * 1024 * 1024 * 1024;
      default: return value;
    }
  }
  
  return 0;
};

// Static CUAD contract data for development
const CUAD_DATA = {
  storage: {
    totalGB: 37.04,
    usedPercent: 85,
    categories: [
      { name: 'Services Agreements', value: 12.5, icon: '/assets/icons/files/ic-pdf.svg' },
      { name: 'NDAs', value: 8.2, icon: '/assets/icons/files/ic-zip.svg' },
      { name: 'Employment Contracts', value: 6.8, icon: '/assets/icons/files/ic-word.svg' },
      { name: 'License Agreements', value: 9.5, icon: '/assets/icons/files/ic-legal.svg' }
    ]
  },
  summary: {
    adls: { title: "Knowledge Domains", value: 4, total: 10, icon: "/assets/icons/files/ic-pdf.svg" },
    docling: { title: "Document Processing", value: 89, total: 128, icon: "/assets/icons/files/ic-tech.svg" },
    aiSearch: { title: "Vector Indexing", value: 76, total: 94, icon: "/assets/icons/files/ic-txt.svg" }
  },
  activity: {
    chartSeries: [
      { 
        name: 'Contracts Indexed', 
        categories: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
        data: [
          { name: 'Jan', data: [12, 19, 8, 15, 22, 18, 25, 14] }
        ]
      },
      { 
        name: 'Documents Processed', 
        categories: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
        data: [
          { name: 'Jan', data: [8, 15, 12, 9, 18, 22, 16, 20] }
        ]
      }
    ]
  },
  folders: [
    { id: 'termination-clauses', name: 'Termination Clauses', count: 156 },
    { id: 'confidentiality', name: 'Confidentiality', count: 89 },
    { id: 'payment-terms', name: 'Payment Terms', count: 67 },
    { id: 'liability', name: 'Liability', count: 45 }
  ],
  recentFiles: [
    { id: 'services-agreement-2024', name: 'Services Agreement 2024.pdf', type: 'PDF', size: 2.4 },
    { id: 'nda-template', name: 'NDA Template.docx', type: 'DOCX', size: '156KB' },
    { id: 'employment-contract', name: 'Employment Contract.pdf', type: 'PDF', size: '1.8MB' },
    { id: 'license-agreement', name: 'License Agreement.docx', type: 'DOCX', size: '234KB' },
    { id: 'ip-assignment', name: 'IP Assignment.pdf', type: 'PDF', size: '3.1MB' }
  ]
};

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
    console.info('CREATE NEW CONTRACT DOMAIN');
  }, [newFolderDialog]);

  const handleDrop = useCallback(
    (acceptedFiles: File[]) => {
      setFiles([...files, ...acceptedFiles]);
    },
    [files]
  );

  const renderStorageOverview = () => (
    <FileStorageOverview
      total={CUAD_DATA.storage.totalGB}
      chart={{ series: CUAD_DATA.storage.usedPercent }}
      data={CUAD_DATA.storage.categories.map(category => ({
        name: category.name,
        usedStorage: category.value,
        filesCount: Math.floor(category.value * 10),
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
      title="Contract Domain Configuration"
      folderName={folderName}
      onChangeFolderName={handleChangeFolderName}
      onCreate={handleCreateNewFolder}
    />
  );

  return (
    <>
      <DashboardContent maxWidth="xl">
        <Typography variant="h4" sx={{ mb: { xs: 3, md: 5 } }}>
          CUAD Contract Management �
        </Typography>
        
        <Grid container spacing={3}>
          <Grid sx={{ display: { xs: 'block', sm: 'none' } }} size={12}>
            {renderStorageOverview()}
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FileWidget
              title="Knowledge Domains"
              value={CUAD_DATA.summary.adls.value}
              total={CUAD_DATA.summary.adls.total}
              icon="/assets/icons/files/ic-document.svg"
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FileWidget
              title="Document Processing"
              value={CUAD_DATA.summary.docling.value}
              total={CUAD_DATA.summary.docling.total}
              icon="/assets/icons/files/ic-pdf.svg"
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FileWidget
              title="Vector Indexing"
              value={CUAD_DATA.summary.aiSearch.value}
              total={CUAD_DATA.summary.aiSearch.total}
              icon="/assets/icons/files/ic-clinical.svg"
            />
          </Grid>

          <Grid size={{ xs: 12, md: 6, lg: 8 }}>
            <FileDataActivity
              title="Contract Indexing Activity"
              chart={{
                series: CUAD_DATA.activity.chartSeries,
              }}
            />

            <Box sx={{ mt: 5 }}>
              <FileManagerPanel
                title="Contract Categories"
                link={paths.dashboard.documents.list}
                onOpen={newFolderDialog.onTrue}
              />

              <Scrollbar sx={{ mb: 3, minHeight: 186 }}>
                <Box sx={{ gap: 3, display: 'flex' }}>
                  {CUAD_DATA.folders.map((folder) => (
                    <FileManagerFolderItem
                      key={folder.id}
                      folder={{
                        id: folder.id,
                        name: folder.name,
                        url: `/contracts/${folder.id}`,
                        size: folder.count,
                        type: 'folder',
                        tags: [],
                        isFavorited: false,
                        createdAt: new Date().toISOString(),
                        modifiedAt: new Date().toISOString(),
                        shared: null
                      }}
                      onDelete={() => console.info('DELETE', folder.id)}
                      sx={{
                        ...(CUAD_DATA.folders.length > 3 && {
                          width: 240,
                          flexShrink: 0,
                        }),
                      }}
                    />
                  ))}
                </Box>
              </Scrollbar>

              <FileManagerPanel
                title="Recently Indexed Contracts"
                link={paths.dashboard.documents.list}
                onOpen={newFilesDialog.onTrue}
              />

              <Box sx={{ gap: 2, display: 'flex', flexDirection: 'column' }}>
                {CUAD_DATA.recentFiles.slice(0, 5).map((file) => (
                  <FileRecentItem
                    key={file.id}
                    file={{
                      id: file.id,
                      name: file.name,
                      url: `/contracts/${file.id}`,
                      type: file.type,
                      size: parseSizeToBytes(file.size),
                      tags: [],
                      isFavorited: false,
                      createdAt: new Date().toISOString(),
                      modifiedAt: new Date().toISOString(),
                      shared: null
                    }}
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
                      Drop CUAD contracts here for indexing (PDF, DOCX, XLSX)
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

            </Box>
          </Grid>
        </Grid>
      </DashboardContent>

      {renderNewFilesDialog()}
      {renderNewFolderDialog()}
    </>
  );
}
