'use client';

import type { IChatConversation } from 'src/types/chat';

import { useEffect, useCallback } from 'react';

import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import { useTheme } from '@mui/material/styles';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import useMediaQuery from '@mui/material/useMediaQuery';

import { paths } from 'src/routes/paths';
import { useRouter } from 'src/routes/hooks';

import { Iconify } from 'src/components/iconify';
import { Scrollbar } from 'src/components/scrollbar';

import { ToggleButton } from './styles';
import { ChatNavItem } from './chat-nav-item';
import { ChatNavItemSkeleton } from './chat-skeleton';

import type { UseNavCollapseReturn } from './hooks/use-collapse-nav';

// ----------------------------------------------------------------------

const NAV_WIDTH = 320;
const NAV_COLLAPSE_WIDTH = 96;

type Props = {
  loading: boolean;
  selectedConversationId: string;
  conversations: {
    allIds: string[];
    byId: Record<string, IChatConversation>;
  };
  collapseNav: UseNavCollapseReturn;
};

export function ChatNav({
  loading,
  collapseNav,
  conversations,
  selectedConversationId,
}: Props) {
  const router = useRouter();
  const theme = useTheme();
  const mdUp = useMediaQuery(theme.breakpoints.up('md'));

  const {
    openMobile,
    onOpenMobile,
    onCloseMobile,
    onCloseDesktop,
    collapseDesktop,
    onCollapseDesktop,
  } = collapseNav;

  const handleCloseNav = useCallback(() => {
    if (mdUp) {
      onCloseDesktop();
    } else {
      onCloseMobile();
    }
  }, [mdUp, onCloseDesktop, onCloseMobile]);

  const handleNewChat = useCallback(() => {
    router.push(paths.dashboard.chat);
  }, [router]);

  const handleToggleNav = useCallback(() => {
    if (mdUp) {
      onCollapseDesktop();
    } else {
      onCloseMobile();
    }
  }, [mdUp, onCloseMobile, onCollapseDesktop]);

  useEffect(() => {
    if (!selectedConversationId) {
      handleCloseNav();
    }
  }, [selectedConversationId, handleCloseNav]);

  useEffect(() => {
    if (!mdUp) {
      onCloseDesktop();
    }
  }, [onCloseDesktop, mdUp]);

  const renderLoading = () => (
    <Box sx={{ p: 2.5 }}>
      <ChatNavItemSkeleton />
    </Box>
  );

  const renderContent = () => (
    <>
      <Box
        sx={{
          p: 2.5,
          pb: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {!collapseDesktop && (
          <Typography variant="h6" sx={{ fontSize: 14, fontWeight: 600 }}>
            Chat History
          </Typography>
        )}

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton onClick={handleToggleNav}>
            <Iconify
              icon={collapseDesktop ? 'eva:arrow-ios-forward-fill' : 'eva:arrow-ios-back-fill'}
            />
          </IconButton>

          {!collapseDesktop && (
            <IconButton onClick={handleNewChat} sx={{ ml: 1 }}>
              <Iconify width={24} icon="solar:plus-circle-bold" />
            </IconButton>
          )}
        </Box>
      </Box>

      {loading ? (
        renderLoading()
      ) : (
        <Scrollbar sx={{ pb: 1 }}>
          <Box sx={{ p: 2.5, pt: 1 }}>
            {conversations.allIds.map((id) => (
              <ChatNavItem
                key={id}
                conversation={conversations.byId[id]}
                selected={id === selectedConversationId}
                onCloseMobile={handleCloseNav}
                onClick={() => router.push(`${paths.dashboard.chat}?id=${id}`)}
                collapse={collapseDesktop}
              />
            ))}
          </Box>
        </Scrollbar>
      )}
    </>
  );

  return (
    <>
      <ToggleButton onClick={onOpenMobile} sx={{ display: { md: 'none' } }}>
        <Iconify width={16} icon="solar:chat-round-dots-bold" />
      </ToggleButton>

      <Box
        sx={{
          minHeight: 0,
          flex: '1 1 auto',
          width: NAV_WIDTH,
          flexDirection: 'column',
          display: { xs: 'none', md: 'flex' },
          borderRight: `solid 1px ${theme.vars.palette.divider}`,
          transition: theme.transitions.create(['width'], {
            duration: theme.transitions.duration.shorter,
          }),
          ...(collapseDesktop && { width: NAV_COLLAPSE_WIDTH }),
        }}
      >
        {renderContent()}
      </Box>

      <Drawer
        open={openMobile}
        onClose={onCloseMobile}
        slotProps={{ backdrop: { invisible: true } }}
        PaperProps={{ sx: { width: NAV_WIDTH } }}
      >
        {renderContent()}
      </Drawer>
    </>
  );
}