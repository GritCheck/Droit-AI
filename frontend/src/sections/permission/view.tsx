'use client';

import { useState, useCallback } from 'react';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import Typography from '@mui/material/Typography';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

import { paths } from 'src/routes/paths';

import { useSecurityGroups } from 'src/hooks/useSecurityGroups';

import { DashboardContent } from 'src/layouts/dashboard';

import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { useMockedUser } from 'src/auth/hooks';

// ----------------------------------------------------------------------

export function PermissionDeniedView() {
  const [role, setRole] = useState('admin');

  const { user } = useMockedUser();
  const { data: securityGroups, loading, error } = useSecurityGroups();

  const handleChangeRole = useCallback(
    (event: React.MouseEvent<HTMLElement>, newRole: string | null) => {
      if (newRole !== null) {
        setRole(newRole);
      }
    },
    []
  );

  // Show loading state
  if (loading) {
    return (
      <DashboardContent>
        <CustomBreadcrumbs
          heading="Security Groups & RLS"
          links={[{ name: 'Dashboard', href: paths.dashboard.root }, { name: 'Access Control' }]}
          sx={{ mb: { xs: 3, md: 5 } }}
        />
        <Box sx={{ textAlign: 'center', py: 10 }}>
          <Typography variant="h4" sx={{ mb: 2 }}>
            Loading security groups...
          </Typography>
        </Box>
      </DashboardContent>
    );
  }

  // Show error state
  if (error || !securityGroups) {
    return (
      <DashboardContent>
        <CustomBreadcrumbs
          heading="Security Groups & RLS"
          links={[{ name: 'Dashboard', href: paths.dashboard.root }, { name: 'Access Control' }]}
          sx={{ mb: { xs: 3, md: 5 } }}
        />
        <Box sx={{ textAlign: 'center', py: 10 }}>
          <Typography variant="h4" sx={{ mb: 2, color: 'error.main' }}>
            Error loading security groups
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>
            {error || 'Unknown error occurred'}
          </Typography>
        </Box>
      </DashboardContent>
    );
  }

  return (
    <DashboardContent>
      <CustomBreadcrumbs
        heading="Security Groups & RLS"
        links={[{ name: 'Dashboard', href: paths.dashboard.root }, { name: 'Access Control' }]}
        sx={{ mb: { xs: 3, md: 5 } }}
      />
      <ToggleButtonGroup
        exclusive
        value={role}
        size="small"
        onChange={handleChangeRole}
        sx={{ mb: 5, alignSelf: 'center' }}
      >
        <ToggleButton value="admin" aria-label="Tier 1: Global Admin (Full Access)">
          Tier 1: Global Admin (Full Access)
        </ToggleButton>
        <ToggleButton value="auditor" aria-label="Tier 2: Compliance Auditor">
          Tier 2: Compliance Auditor
        </ToggleButton>
        <ToggleButton value="user" aria-label="Tier 3: Departmental (Restricted Access)">
          Tier 3: Departmental (Restricted Access)
        </ToggleButton>
      </ToggleButtonGroup>

      {typeof role !== 'undefined' && (user?.role === role || role === 'admin') ? (
        <Box sx={{ gap: 3, display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)' }}>
          {securityGroups.map((group, index) => (
            <Card key={index}>
              <CardHeader title={group.title} subheader={group.subheader} />
              <Typography variant="body2" sx={{ px: 3, py: 2, color: 'text.secondary' }}>
                {group.filter}
              </Typography>
            </Card>
          ))}
        </Box>
      ) : (
        <Box sx={{ textAlign: 'center', py: 10 }}>
          <Typography variant="h4" sx={{ mb: 2, color: 'error.main' }}>
            Insufficient Clearance Level
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>
            RLS Policy &apos;deny_all_external&apos; is active.
          </Typography>
        </Box>
      )}
    </DashboardContent>
  );
}
