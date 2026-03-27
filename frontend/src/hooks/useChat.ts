'use client';

import type { ChatRequest, ChatResponse } from 'src/types/chat';

import { useState, useCallback } from 'react';

import { CONFIG } from 'src/global-config';
import axiosInstance, { endpoints } from 'src/lib/axios';

// ----------------------------------------------------------------------

export function useChat() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [streamingText, setStreamingText] = useState<string>('');

  const askQuestion = useCallback(async (request: ChatRequest, useStreaming: boolean = true): Promise<ChatResponse> => {
    try {
      setLoading(true);
      setError(null);
      setStreamingText('');

      if (useStreaming) {
        // Use streaming endpoint
        const streamResponse = await fetch(`${CONFIG.serverUrl}${endpoints.chat.queryStream}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('azure_access_token')}`,
          },
          body: JSON.stringify(request),
        });

        if (!streamResponse.ok) {
          throw new Error('Stream request failed');
        }

        const reader = streamResponse.body?.getReader();
        const decoder = new TextDecoder();
        let fullResponse: ChatResponse | null = null;

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                
                if (data === '[DONE]') {
                  break;
                }

                try {
                  const parsed = JSON.parse(data);
                  
                  if (parsed.type === 'token') {
                    setStreamingText(prev => prev + parsed.content);
                  } else if (parsed.type === 'complete') {
                    fullResponse = parsed.result;
                    setResponse(fullResponse);
                  } else if (parsed.type === 'error') {
                    throw new Error(parsed.error);
                  }
                } catch (e) {
                  // Ignore parsing errors for malformed chunks
                }
              }
            }
          }
        }

        if (!fullResponse) {
          throw new Error('No response received');
        }

        return fullResponse;
      } else {
        // Use regular endpoint
        const chatResponse = await axiosInstance.post('/api/v1/chat/query', request);
        const data = chatResponse.data as ChatResponse;
        setResponse(data);
        return data;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    response,
    streamingText,
    askQuestion,
    clearError,
  };
}
