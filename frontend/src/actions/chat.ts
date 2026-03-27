import type { SWRConfiguration } from 'swr';
import type { IChatMessage, IChatConversation } from 'src/types/chat';

import { useMemo } from 'react';
import { keyBy } from 'es-toolkit';
import { v4 as uuidv4 } from 'uuid';
import useSWR, { mutate } from 'swr';
import { isAxiosError } from 'axios';

import axios, { fetcher, endpoints } from 'src/lib/axios';

// ----------------------------------------------------------------------

const enableServer = true;

const CHAT_ENDPOINT = endpoints.chat.query;

const swrOptions: SWRConfiguration = {
  revalidateIfStale: enableServer,
  revalidateOnFocus: enableServer,
  revalidateOnReconnect: enableServer,
};




// ----------------------------------------------------------------------

type ConversationsData = {
  conversations: IChatConversation[];
};

export function useGetConversations() {
  const url = `${CHAT_ENDPOINT}/conversations`;

  const { data, isLoading, error, isValidating } = useSWR<ConversationsData>(
    url,
    fetcher,
    swrOptions
  );

  const memoizedValue = useMemo(() => {
    const byId = data?.conversations.length ? keyBy(data.conversations, (option) => option.id) : {};
    const allIds = Object.keys(byId);

    return {
      conversations: { byId, allIds },
      conversationsLoading: isLoading,
      conversationsError: error,
      conversationsValidating: isValidating,
      conversationsEmpty: !isLoading && !isValidating && !allIds.length,
    };
  }, [data?.conversations, error, isLoading, isValidating]);

  return memoizedValue;
}

// ----------------------------------------------------------------------

type ConversationData = {
  conversation: IChatConversation;
};

export function useGetConversation(conversationId: string) {
  const url = conversationId ? `${CHAT_ENDPOINT}/conversation/${conversationId}` : '';

  const { data, isLoading, error, isValidating } = useSWR<ConversationData>(
    url,
    fetcher,
    swrOptions
  );

  const memoizedValue = useMemo(
    () => ({
      conversation: data?.conversation,
      conversationLoading: isLoading,
      conversationError: error,
      conversationValidating: isValidating,
      conversationEmpty: !isLoading && !isValidating && !data?.conversation,
    }),
    [data?.conversation, error, isLoading, isValidating]
  );

  return memoizedValue;
}

// ----------------------------------------------------------------------

export async function sendMessage(conversationId: string, messageData: IChatMessage) {
  try {
    // Use the correct backend API endpoint for sending messages
    const response = await axios.post(`${CHAT_ENDPOINT}/ask`, {
      conversation_id: conversationId,
      message: messageData.body,
      // Add any other required fields for the backend
    });
    
    return response.data;
  } catch (error) {
    console.error('Failed to send message:', error);
    throw error;
  }
}

// ----------------------------------------------------------------------

export async function createConversation(conversationData: IChatConversation) {
  try {
    // For new conversations, we can start by asking a question directly
    // The backend will create the conversation automatically
    const response = await axios.post(`${CHAT_ENDPOINT}/ask`, {
      message: conversationData.messages[0]?.body || "Hello",
      // The backend will create a new conversation ID
    });
    
    return {
      conversation: {
        ...conversationData,
        id: response.data.conversation_id || uuidv4()
      }
    };
  } catch (error) {
    console.error('Failed to create conversation:', error);
    
    // Handle specific error cases
    if (isAxiosError(error)) {
      const errorMessage = error.response?.data?.detail || error.message;
      
      // Check if it's a search index error
      if (errorMessage.includes('index') && errorMessage.includes('was not found')) {
        throw new Error('Search service is not configured yet. Please contact your administrator to set up the search index.');
      }
      
      // Check if it's an authentication error
      if (error.response?.status === 401) {
        throw new Error('Authentication failed. Please sign in again.');
      }
      
      // Check if it's a server error
      if (error.response?.status && error.response.status >= 500) {
        throw new Error('Service temporarily unavailable. Please try again later.');
      }
      
      throw new Error(errorMessage || 'Failed to create conversation');
    }
    
    // Handle non-Axios errors
    if (error instanceof Error) {
      throw error;
    }
    
    throw new Error('Failed to create conversation');
  }
}

// ----------------------------------------------------------------------

export async function clickConversation(conversationId: string) {
  /**
   * Work on server
   */
  if (enableServer) {
    await axios.get(CHAT_ENDPOINT, { params: { conversationId, endpoint: 'mark-as-seen' } });
  }

  /**
   * Work in local
   */

  mutate(
    `${CHAT_ENDPOINT}/conversations`,
    (currentData: ConversationsData | undefined) => {
      if (!currentData) return { conversations: [] };
      
      const currentConversations: IChatConversation[] = currentData.conversations;

      const conversations = currentConversations.map((conversation: IChatConversation) =>
        conversation.id === conversationId ? { ...conversation, unreadCount: 0 } : conversation
      );

      return { ...currentData, conversations };
    },
    false
  );
}
