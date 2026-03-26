'use client';

import { useEffect, startTransition } from 'react';

import Typography from '@mui/material/Typography';

import { paths } from 'src/routes/paths';
import { useRouter, useSearchParams } from 'src/routes/hooks';

import { CONFIG } from 'src/global-config';
import { DashboardContent } from 'src/layouts/dashboard';
import { useGetConversation, useGetConversations } from 'src/actions/chat';

import { EmptyContent } from 'src/components/empty-content';

import { useAuthContext } from 'src/auth/hooks';

import { ChatNav } from '../chat-nav';
import { ChatLayout } from '../layout';
import { ChatRoom } from '../chat-room';
import { ChatMessageList } from '../chat-message-list';
import { ChatMessageInput } from '../chat-message-input';
import { ChatHeaderDetail } from '../chat-header-detail';
import { useCollapseNav } from '../hooks/use-collapse-nav';

// ----------------------------------------------------------------------

export function ChatView() {
  const router = useRouter();
  const { user } = useAuthContext();

  const searchParams = useSearchParams();
  const selectedConversationId = searchParams.get('id') || '';

  const { conversations, conversationsLoading } = useGetConversations();
  const { conversation, conversationError, conversationLoading } =
    useGetConversation(selectedConversationId);

  const roomNav = useCollapseNav();
  const conversationsNav = useCollapseNav();

  useEffect(() => {
    if (conversationError) {
      startTransition(() => {
        router.push(paths.dashboard.chat);
      });
    }
  }, [conversationError, router]);

  // For RAG, we don't need to filter other human participants, 
  // but we keep the logic compatible with the header component.
  const filteredParticipants = conversation
    ? conversation.participants.filter((p) => p.id !== `${user?.id}`)
    : [];

  const hasConversation = !!selectedConversationId && !!conversation;

  return (
    <DashboardContent
      maxWidth={false}
      sx={{ display: 'flex', flex: '1 1 auto', flexDirection: 'column' }}
    >
      <Typography variant="h4" sx={{ mb: { xs: 3, md: 5 } }}>
        AI Assistant Chat
      </Typography>

      <ChatLayout
        slots={{
          header: hasConversation ? (
            <ChatHeaderDetail
              collapseNav={roomNav}
              participants={filteredParticipants}
              loading={conversationLoading}
            />
          ) : null,
          nav: (
            <ChatNav
              conversations={conversations}
              selectedConversationId={selectedConversationId}
              collapseNav={conversationsNav}
              loading={conversationsLoading}
            />
          ),
          main: (
            <>
              {selectedConversationId ? (
                conversationError ? (
                  <EmptyContent
                    title={conversationError.message}
                    imgUrl={`${CONFIG.assetsDir}/assets/icons/empty/ic-chat-empty.svg`}
                  />
                ) : (
                  <ChatMessageList
                    messages={conversation?.messages ?? []}
                    participants={filteredParticipants}
                    loading={conversationLoading}
                  />
                )
              ) : (
                <EmptyContent
                  title="Start a conversation"
                  description="Ask questions about your documents and get AI-powered responses"
                  imgUrl={`${CONFIG.assetsDir}/assets/icons/empty/ic-chat-active.svg`}
                />
              )}

              <ChatMessageInput
                disabled={false}
                selectedConversationId={selectedConversationId}
              />
            </>
          ),
          details: hasConversation && (
            <ChatRoom
              collapseNav={roomNav}
              participants={filteredParticipants}
              loading={conversationLoading}
              messages={conversation?.messages ?? []}
            />
          ),
        }}
      />
    </DashboardContent>
  );
}