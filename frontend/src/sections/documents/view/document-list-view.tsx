'use client';

import type { TableHeadCellProps } from 'src/components/table';
import type { IDocumentItem, IDocumentTableFilters } from 'src/types/document';

import { varAlpha } from 'minimal-shared/utils';
import { useState, useEffect, useCallback } from 'react';
import { useBoolean, useSetState } from 'minimal-shared/hooks';

import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Card from '@mui/material/Card';
import Table from '@mui/material/Table';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import TableBody from '@mui/material/TableBody';
import IconButton from '@mui/material/IconButton';

import { paths } from 'src/routes/paths';
import { RouterLink } from 'src/routes/components';

import { _roles } from 'src/_mock';
import { _documents } from 'src/_mock/_documents';
import { DashboardContent } from 'src/layouts/dashboard';

import { Label } from 'src/components/label';
import { toast } from 'src/components/snackbar';
import { Iconify } from 'src/components/iconify';
import { Scrollbar } from 'src/components/scrollbar';
import { ConfirmDialog } from 'src/components/custom-dialog';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';
import {
  useTable,
  emptyRows,
  rowInPage,
  TableNoData,
  getComparator,
  TableEmptyRows,
  TableHeadCustom,
  TableSelectedAction,
  TablePaginationCustom,
} from 'src/components/table';

import { DocumentTableRow } from '../document-table-row';
import { DocumentTableToolbar } from '../document-table-toolbar';
import { DocumentTableFiltersResult } from '../document-table-filters-result';

// ----------------------------------------------------------------------

const STATUS_OPTIONS = [
  { value: 'all', label: 'All' },
  { value: 'indexed', label: 'Indexed' },
  { value: 'processing', label: 'Processing' },
  { value: 'failed', label: 'Failed' },
  { value: 'flagged', label: 'Flagged' }
];

const TABLE_HEAD: TableHeadCellProps[] = [
  { id: 'name', label: 'Document Name' },
  { id: 'data_limit', label: 'Chunk Size (tokens)', width: 120 },
  { id: 'rate_limit', label: 'Vector Dimensions', width: 120 },
  { id: 'status', label: 'Index Status', width: 100 },
  { id: 'time_limit', label: 'Last Synced', width: 120 },
  { id: 'price', label: 'Security Level (RLS)', width: 140 },
  { id: 'Actions', width: 88 }, // for actions (edit/delete)
];

// ----------------------------------------------------------------------

export function KnowledgeBaseManager() {
  const table = useTable();
  const confirmDialog = useBoolean();

  // TODO: Integrate with Azure AI Search API for document fetching
  const tableData = _documents;
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Placeholder functions for API integration
  const handleFetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching documents from Azure AI Search API...');
      // TODO: Replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDelete = useCallback(async (document: any) => {
    try {
      console.log('Deleting document from vector index:', document.id);
      // TODO: Replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete document');
    }
  }, []);

  // Fetch documents on mount
  useEffect(() => {
    handleFetch();
  }, [handleFetch]);

  // Show error toast when there's an error
  useEffect(() => {
    if (error) {
      toast.error(error);
    }
  }, [error]);

  const filters = useSetState<IDocumentTableFilters>({ name: '', type: [], status: 'all' });
  const { state: currentFilters, setState: updateFilters } = filters;

  const dataFiltered = applyFilter({
    inputData: tableData,
    comparator: getComparator(table.order, table.orderBy),
    filters: currentFilters,
  });

  const dataInPage = rowInPage(dataFiltered, table.page, table.rowsPerPage);

  const canReset =
    !!currentFilters.name || currentFilters.type.length > 0 || currentFilters.status !== 'all';

  const notFound = (!dataFiltered.length && canReset) || !dataFiltered.length;

  // Delete a single row using placeholder function
  const handleDeleteRow = useCallback(
    async (id: string) => {
      const docToDelete = tableData.find((row: { id: string; }) => row.id === id);
      if (!docToDelete) return;
      try {
        await handleDelete(docToDelete);
        toast.success('Document removed from vector index!');
        table.onUpdatePageDeleteRow(dataInPage.length);
      } catch {
        toast.error('Failed to remove document!');
      }
    },
    [tableData, handleDelete, table, dataInPage.length]
  );

  // Delete selected rows using placeholder function
  const handleDeleteRows = useCallback(async () => {
    const docsToDelete = tableData.filter((row: { id: string; }) => table.selected.includes(row.id));
    if (docsToDelete.length === 0) return;
    try {
      await Promise.all(docsToDelete.map((doc: { id: string; }) => handleDelete(doc)));
      toast.success('Documents removed from vector index!');
      table.onUpdatePageDeleteRows(dataInPage.length, dataFiltered.length);
    } catch {
      toast.error('Failed to remove documents!');
    }
  }, [tableData, table, dataInPage.length, dataFiltered.length, handleDelete]);

  const handleFilterStatus = useCallback(
    (event: React.SyntheticEvent, newValue: string) => {
      table.onResetPage();
      updateFilters({ status: newValue });
    },
    [updateFilters, table]
  );

  const renderConfirmDialog = () => (
    <ConfirmDialog
      open={confirmDialog.value}
      onClose={confirmDialog.onFalse}
      title="Remove Documents"
      content={
        <>
          Are you sure you want to remove these documents from the vector index?
        </>
      }
      action={
        <Button
          variant="contained"
          color="error"
          onClick={() => {
            handleDeleteRows();
            confirmDialog.onFalse();
          }}
        >
          Remove
        </Button>
      }
    />
  );

  return (
    <>
      <DashboardContent>
        <CustomBreadcrumbs
          heading="Document Registry"
          links={[
            { name: 'Dashboard', href: paths.dashboard.root },
            { name: 'Knowledge Base', href: paths.dashboard.fileManager },
            { name: 'Document Registry' },
          ]}
          action={
            <Button
              component={RouterLink}
              href={paths.dashboard.documents.new}
              variant="contained"
              startIcon={<Iconify icon="mingcute:add-line" />}
            >
              Ingest New Document
            </Button>
          }
          sx={{ mb: { xs: 3, md: 5 } }}
        />

        <Card>
          <Tabs
            value={currentFilters.status}
            onChange={handleFilterStatus}
            sx={[
              (theme) => ({
                px: 2.5,
                boxShadow: `inset 0 -2px 0 0 ${varAlpha(theme.vars.palette.grey['500Channel'], 0.08)}`,
              }),
            ]}
          >
            {STATUS_OPTIONS.map((tab) => (
              <Tab
                key={tab.value}
                iconPosition="end"
                value={tab.value}
                label={tab.label}
                icon={
                  <Label
                    variant={
                      ((tab.value === 'all' || tab.value === currentFilters.status) && 'filled') ||
                      'soft'
                    }
                    color={
                      (tab.value === 'indexed' && 'success') ||
                      (tab.value === 'processing' && 'warning') ||
                      (tab.value === 'failed' && 'error') ||
                      (tab.value === 'flagged' && 'info') ||
                      'default'
                    }
                  >
                    {['indexed', 'processing', 'failed', 'flagged'].includes(tab.value)
                      ? tableData.filter((doc) => doc.status === tab.value).length
                      : tableData.length}
                  </Label>
                }
              />
            ))}
          </Tabs>

          {/* <DocumentTableToolbar
            filters={filters}
            onResetPage={table.onResetPage}
            options={{ roles: _roles }}
          /> */}

          {canReset && (
            <DocumentTableFiltersResult
              filters={filters}
              totalResults={dataFiltered.length}
              onResetPage={table.onResetPage}
              sx={{ p: 2.5, pt: 0 }}
            />
          )}

          <Box sx={{ position: 'relative' }}>
            <TableSelectedAction
              dense={table.dense}
              numSelected={table.selected.length}
              rowCount={dataFiltered.length}
              onSelectAllRows={(checked) =>
                table.onSelectAllRows(
                  checked,
                  dataFiltered.map((row) => row.id)
                )
              }
              action={
                <Tooltip title="Delete">
                  <IconButton color="primary" onClick={confirmDialog.onTrue}>
                    <Iconify icon="solar:trash-bin-trash-bold" />
                  </IconButton>
                </Tooltip>
              }
            />

            <Scrollbar>
              <Table size={table.dense ? 'small' : 'medium'} sx={{ minWidth: 960 }}>
                <TableHeadCustom
                  order={table.order}
                  orderBy={table.orderBy}
                  headCells={TABLE_HEAD}
                  rowCount={dataFiltered.length}
                  numSelected={table.selected.length}
                  onSort={table.onSort}
                  onSelectAllRows={(checked) =>
                    table.onSelectAllRows(
                      checked,
                      dataFiltered.map((row) => row.id)
                    )
                  }
                />

                <TableBody>
                  {dataFiltered
                    .slice(
                      table.page * table.rowsPerPage,
                      table.page * table.rowsPerPage + table.rowsPerPage
                    )
                    .map((row) => (
                      <DocumentTableRow
                        key={row.id}
                        row={row}
                        selected={table.selected.includes(row.id)}
                        onSelectRow={() => table.onSelectRow(row.id)}
                        onDeleteRow={() => handleDeleteRow(row.id)}
                        editHref={paths.dashboard.documents.edit(row.id)}
                      />
                    ))}

                  <TableEmptyRows
                    height={table.dense ? 56 : 56 + 20}
                    emptyRows={emptyRows(table.page, table.rowsPerPage, dataFiltered.length)}
                  />

                  <TableNoData notFound={notFound} />
                </TableBody>
              </Table>
            </Scrollbar>
          </Box>

          <TablePaginationCustom
            page={table.page}
            dense={table.dense}
            count={dataFiltered.length}
            rowsPerPage={table.rowsPerPage}
            onPageChange={table.onChangePage}
            onChangeDense={table.onChangeDense}
            onRowsPerPageChange={table.onChangeRowsPerPage}
          />
        </Card>
      </DashboardContent>

      {renderConfirmDialog()}
    </>
  );
}

// ----------------------------------------------------------------------

type ApplyFilterProps = {
  inputData: IDocumentItem[];
  filters: IDocumentTableFilters;
  comparator: (a: any, b: any) => number;
};

function applyFilter({ inputData, comparator, filters }: ApplyFilterProps) {
  const { name, status, type } = filters;

  const stabilizedThis = inputData.map((el, index) => [el, index] as const);

  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });

  inputData = stabilizedThis.map((el) => el[0]);

  if (name) {
    inputData = inputData.filter((documentItem) => documentItem.name.toLowerCase().includes(name.toLowerCase()));
  }

  if (status !== 'all') {
    inputData = inputData.filter((documentItem) => documentItem.status === status);
  }

  if (type.length) {
    inputData = inputData.filter((documentItem) => type.includes(documentItem.type));
  }

  return inputData;
}
