'use client';

import { useState, useCallback } from 'react';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import Typography from '@mui/material/Typography';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

import { paths } from 'src/routes/paths';

import { DashboardContent } from 'src/layouts/dashboard';

import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';

import { useMockedUser } from 'src/auth/hooks';

// ----------------------------------------------------------------------

export function PermissionDeniedView() {
  const [role, setRole] = useState('admin');

  const { user } = useMockedUser();

  const handleChangeRole = useCallback(
    (event: React.MouseEvent<HTMLElement>, newRole: string | null) => {
      if (newRole !== null) {
        setRole(newRole);
      }
    },
    []
  );

  const securityGroups = [
    { title: "HR & Benefits", subheader: "Azure AD Group: hr-all-staff", filter: "Entitlement Filter: (security_group eq 'HR') and (clearance_level ge 2). This group grants read access to employee records and benefits administration." },
    { title: "Legal & Contracts", subheader: "Azure AD Group: legal-exec", filter: "Entitlement Filter: (security_group eq 'Legal') and (clearance_level ge 4). This group grants read access to all legal archives and binding contracts." },
    { title: "Financial Audits", subheader: "Azure AD Group: finance-mgr", filter: "Entitlement Filter: (security_group eq 'Finance') and (clearance_level ge 3). This group grants access to financial statements and audit reports." },
    { title: "Operational SOPs", subheader: "Azure AD Group: ops-field", filter: "Entitlement Filter: (security_group eq 'Operations') and (clearance_level ge 2). This group grants access to standard operating procedures and field guides." },
    { title: "Clinical Data", subheader: "Azure AD Group: medical-vetted", filter: "Entitlement Filter: (security_group eq 'Clinical') and (clearance_level ge 5). This group grants access to patient data and clinical research with HIPAA compliance." },
    { title: "Internal Strategy", subheader: "Azure AD Group: board-only", filter: "Entitlement Filter: (security_group eq 'Strategy') and (clearance_level ge 6). This group grants access to board-level strategic planning and confidential initiatives." },
    { title: "Public Relations", subheader: "Azure AD Group: external-comm", filter: "Entitlement Filter: (security_group eq 'Communications') and (clearance_level ge 3). This group grants access to press releases and external communications." },
    { title: "Research & Development", subheader: "Azure AD Group: rnd-team", filter: "Entitlement Filter: (security_group eq 'R&D') and (clearance_level ge 4). This group grants access to proprietary research and development documentation." },
  ];

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
