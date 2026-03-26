'use client';

import { useRef, useMemo, useState, useCallback } from 'react';

import Box from '@mui/material/Box';
import InputBase from '@mui/material/InputBase';
import IconButton from '@mui/material/IconButton';

import { paths } from 'src/routes/paths';
import { useRouter } from 'src/routes/hooks';

import { today } from 'src/utils/format-time';

import { sendMessage, createConversation } from 'src/actions/chat';

import { Iconify } from 'src/components/iconify';

import { useMockedUser } from 'src/auth/hooks';

import { initialConversation } from './utils/initial-conversation';

// ----------------------------------------------------------------------

type Props = {
  disabled: boolean;
  selectedConversationId: string;
};

export function ChatMessageInput({ disabled, selectedConversationId }: Props) {
  const router = useRouter();

  const { user } = useMockedUser();

  const fileRef = useRef<HTMLInputElement>(null);

  const [message, setMessage] = useState('');

  const myContact = useMemo(
    () => ({
      id: `${user?.id}`,
      role: `${user?.role}`,
      email: `${user?.email}`,
      address: `${user?.address}`,
      name: `${user?.displayName}`,
      lastActivity: today(),
      avatarUrl: `${user?.photoURL}`,
      phoneNumber: `${user?.phoneNumber}`,
      status: 'online' as const,
    }),
    [user]
  );

  // FIXED: Recipients is now an empty array because this is a RAG/AI chat
  const { messageData, conversationData } = initialConversation({
    message,
    recipients: [], 
    me: myContact,
  });

  const handleAttach = useCallback(() => {
    if (fileRef.current) {
      fileRef.current.click();
    }
  }, []);

  const handleChangeMessage = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(event.target.value);
  }, []);

  const handleSendMessage = useCallback(
    async (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (event.key !== 'Enter' || !message.trim()) return;

      try {
        if (selectedConversationId) {
          // If the session already exists
          await sendMessage(selectedConversationId, messageData);
        } else {
          // If starting a brand new AI session
          const res = await createConversation(conversationData);
          router.push(`${paths.dashboard.chat}?id=${res.conversation.id}`);
        }
      } catch (error) {
        console.error('Failed to send message:', error);
      } finally {
        setMessage('');
      }
    },
    [conversationData, message, messageData, router, selectedConversationId]
  );

  return (
    <>
      <InputBase
        name="chat-message"
        id="chat-message-input"
        value={message}
        onKeyUp={handleSendMessage}
        onChange={handleChangeMessage}
        placeholder="Type a message..."
        disabled={disabled}
        startAdornment={
          <IconButton>
            <Iconify icon="eva:smiling-face-fill" />
          </IconButton>
        }
        endAdornment={
          <Box sx={{ flexShrink: 0, display: 'flex' }}>
            <IconButton onClick={handleAttach}>
              <Iconify icon="solar:gallery-add-bold" />
            </IconButton>
            <IconButton onClick={handleAttach}>
              <Iconify icon="eva:attach-2-fill" />
            </IconButton>
            <IconButton>
              <Iconify icon="solar:microphone-bold" />
            </IconButton>
          </Box>
        }
        sx={{
          px: 1,
          height: 56,
          flexShrink: 0,
          borderTop: (theme) => `solid 1px ${theme.vars.palette.divider}`,
        }}
      />

      <input type="file" ref={fileRef} style={{ display: 'none' }} />
    </>
  );
}