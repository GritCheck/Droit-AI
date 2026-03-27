'use client';

import type { TableHeadCellProps } from 'src/components/table';
import type { IDocumentTableFilters } from 'src/types/document';

import { useBoolean, useSetState } from 'minimal-shared/hooks';
import { useRef, useMemo, useEffect, useCallback } from 'react';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Table from '@mui/material/Table';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import TableBody from '@mui/material/TableBody';
import IconButton from '@mui/material/IconButton';

import { paths } from 'src/routes/paths';
import { RouterLink } from 'src/routes/components';

import { useDocuments, useDocumentOperations } from 'src/hooks/useDocuments';

import { _roles } from 'src/_mock';
import { DashboardContent } from 'src/layouts/dashboard';

import { toast } from 'src/components/snackbar';
import { Iconify } from 'src/components/iconify';
import { Scrollbar } from 'src/components/scrollbar';
import { ConfirmDialog } from 'src/components/custom-dialog';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';
import {
  useTable,
  emptyRows,
  TableNoData,
  TableEmptyRows,
  TableHeadCustom,
  TableSelectedAction,
  TablePaginationCustom,
} from 'src/components/table';

import { DocumentTableRow } from '../document-table-row';
import { DocumentTableToolbar } from '../document-table-toolbar';
import { DocumentTableFiltersResult } from '../document-table-filters-result';

// ----------------------------------------------------------------------

// Status options removed - backend doesn't provide document status

const TABLE_HEAD: TableHeadCellProps[] = [
  { id: 'name', label: 'Document Name' },
  { id: 'size', label: 'Size (bytes)', width: 120 },
  { id: 'created_at', label: 'Created At', width: 180 },
  { id: 'Actions', width: 88 }, // for actions (view/delete)
];

// ----------------------------------------------------------------------

export function KnowledgeBaseManager() {
  const table = useTable();
  const confirmDialog = useBoolean();
  const tableRef = useRef(table);

  // Update ref when table changes
  useEffect(() => {
    tableRef.current = table;
  }, [table]);

  const filters = useSetState<IDocumentTableFilters>({ name: '', type: [], status: 'all' });
  const { state: currentFilters } = filters;

  // Use API hooks instead of static data - initialize with empty filters first
  const { data: tableData, error, total } = useDocuments();
  const { loading: operationLoading } = useDocumentOperations();

  // Show error toast when there's an error
  useEffect(() => {
    if (error) {
      toast.error(error);
    }
  }, [error]);

  // Use server-side filtered data directly - no client-side filtering needed
  const dataFiltered = useMemo(() => tableData || [], [tableData]);

  const canReset =
    !!currentFilters.name || currentFilters.type.length > 0 || currentFilters.status !== 'all';

  const notFound = (!dataFiltered.length && canReset) || !dataFiltered.length;

  // Delete a single row - not implemented yet
  const handleDeleteRow = useCallback(
    async (id: string) => {
      toast.error('Delete operation not yet implemented');
    },
    []
  );

  // Delete selected rows - not implemented yet
  const handleDeleteRows = useCallback(async () => {
    toast.error('Delete operation not yet implemented');
  }, []);

  // Status filter functionality removed - backend doesn't provide document status

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
          disabled={operationLoading}
          startIcon={operationLoading ? <Iconify icon="mingcute:loading-line" sx={{ animation: 'spin 1s linear infinite' }} /> : null}
        >
          {operationLoading ? 'Removing...' : 'Remove'}
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
          {/* Status tabs removed - backend doesn't provide document status */}

          <DocumentTableToolbar
            filters={filters}
            onResetPage={table.onResetPage}
            options={{ roles: _roles }}
          />

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
                  dataFiltered?.map((row) => row?.id).filter(Boolean) || []
                )
              }
              action={
                <Tooltip title={operationLoading ? "Deleting..." : "Delete"}>
                  <IconButton 
                    color="primary" 
                    onClick={confirmDialog.onTrue}
                    disabled={operationLoading}
                  >
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
                  onSort={table.onSort && table.onSort}
                  onSelectAllRows={table.onSelectAllRows && ((checked) =>
                    table.onSelectAllRows(
                      checked,
                      dataFiltered?.map((row) => row?.id).filter(Boolean) || []
                    )
                  )}
                />

                <TableBody>
                  {(dataFiltered || [])
                    .slice(
                      table.page * table.rowsPerPage,
                      table.page * table.rowsPerPage + table.rowsPerPage
                    )
                    .filter((row): row is NonNullable<typeof row> => row != null)
                    .map((row) => (
                      <DocumentTableRow
                        key={row?.id || `row-${Math.random()}`}
                        row={row}
                        selected={table.selected.includes(row?.id || '')}
                        onSelectRow={() => row?.id && table.onSelectRow(row.id)}
                        onDeleteRow={() => row?.id && handleDeleteRow(row.id)}
                        editHref={row?.id ? paths.dashboard.documents.edit(row.id) : '#'}
                      />
                    ))}

                  <TableEmptyRows
                    height={table.dense ? 56 : 56 + 20}
                    emptyRows={emptyRows(table.page, table.rowsPerPage, total || 0)}
                  />

                  <TableNoData notFound={notFound} />
                </TableBody>
              </Table>
            </Scrollbar>
          </Box>

          <TablePaginationCustom
            page={table.page}
            dense={table.dense}
            count={total || 0} // Use server-side total count
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
