/**
 * useChat Hook - React hook for RAG chat functionality
 * Handles streaming responses, citations, and OBO authentication
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { useSession } from 'next-auth/react';

// Types for chat responses
export interface Citation {
  source_id: string;
  title: string;
  source_link?: string;
  page_number?: number;
  chunk_id?: string;
  relevance_score: number;
  quote_snippet: string;
  confidence: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
  confidence_score?: number;
  safety_passed?: boolean;
  safety_reason?: string;
  follow_up_questions?: string[];
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  generation_time?: number;
  model_used?: string;
  grounding_sources?: string[];
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  metrics: {
    totalTokens: number;
    averageLatency: number;
    safetyViolations: number;
    groundingScore: number;
  };
}

export interface ChatOptions {
  conversationId?: string;
  includeFollowUp?: boolean;
  maxDocuments?: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export function useChat(options: ChatOptions = {}) {
  const { data: session } = useSession();
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
    conversationId: options.conversationId || null,
    metrics: {
      totalTokens: 0,
      averageLatency: 0,
      safetyViolations: 0,
      groundingScore: 0,
    },
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const latencyHistoryRef = useRef<number[]>([]);

  // Calculate metrics
  useEffect(() => {
    const totalMessages = state.messages.filter(m => m.role === 'assistant').length;
    const safeMessages = state.messages.filter(m => m.safety_passed !== false).length;
    const groundedMessages = state.messages.filter(m => m.citations && m.citations.length > 0).length;
    
    const groundingScore = totalMessages > 0 ? (groundedMessages / totalMessages) * 100 : 0;
    const averageLatency = latencyHistoryRef.current.length > 0 
      ? latencyHistoryRef.current.reduce((a, b) => a + b, 0) / latencyHistoryRef.current.length 
      : 0;

    setState(prev => ({
      ...prev,
      metrics: {
        ...prev.metrics,
        groundingScore,
        averageLatency,
      }
    }));
  }, [state.messages]);

  const sendMessage = useCallback(async (message: string) => {
    if (!session?.accessToken) {
      setState(prev => ({ ...prev, error: 'Not authenticated' }));
      return;
    }

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    // Cancel any existing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    const startTime = Date.now();

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.accessToken}`,
        },
        body: JSON.stringify({
          message,
          conversation_id: state.conversationId,
          include_follow_up: options.includeFollowUp ?? true,
          max_documents: options.maxDocuments ?? 10,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      const endTime = Date.now();
      const latency = endTime - startTime;
      latencyHistoryRef.current.push(latency);

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: data.message_id,
        role: 'assistant',
        content: data.answer,
        timestamp: new Date(data.timestamp),
        citations: data.citations,
        confidence_score: data.confidence_score,
        safety_passed: data.safety_passed,
        safety_reason: data.safety_reason,
        follow_up_questions: data.follow_up_questions,
        token_usage: data.token_usage,
        generation_time: data.generation_time,
        model_used: data.model_used,
        grounding_sources: data.grounding_sources,
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        conversationId: data.conversation_id,
        isLoading: false,
        metrics: {
          ...prev.metrics,
          totalTokens: prev.metrics.totalTokens + (data.token_usage?.total_tokens || 0),
          safetyViolations: data.safety_passed === false ? prev.metrics.safetyViolations + 1 : prev.metrics.safetyViolations,
        },
      }));

    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        // Request was cancelled, don't show error
        return;
      }

      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
    }
  }, [session?.accessToken, state.conversationId, options]);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setState(prev => ({ ...prev, isLoading: false }));
  }, []);

  const clearMessages = useCallback(() => {
    setState(prev => ({
      ...prev,
      messages: [],
      conversationId: null,
      error: null,
      metrics: {
        totalTokens: 0,
        averageLatency: 0,
        safetyViolations: 0,
        groundingScore: 0,
      },
    }));
    latencyHistoryRef.current = [];
  }, []);

  const submitFeedback = useCallback(async (messageId: string, rating: number, feedbackType: string, comment?: string) => {
    if (!session?.accessToken) return;

    try {
      await fetch(`${API_BASE_URL}/api/v1/chat/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.accessToken}`,
        },
        body: JSON.stringify({
          message_id: messageId,
          conversation_id: state.conversationId,
          user_id: session.user?.id,
          rating,
          feedback_type: feedbackType,
          comment,
          timestamp: new Date().toISOString(),
        }),
      });
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  }, [session?.accessToken, session?.user?.id, state.conversationId]);

  const retryMessage = useCallback(async (messageId: string) => {
    const messageIndex = state.messages.findIndex(m => m.id === messageId);
    if (messageIndex === -1) return;

    const message = state.messages[messageIndex];
    if (message.role !== 'user') return;

    // Remove the failed assistant response and retry
    setState(prev => ({
      ...prev,
      messages: prev.messages.slice(0, messageIndex + 1),
    }));

    await sendMessage(message.content);
  }, [state.messages, sendMessage]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    // State
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    conversationId: state.conversationId,
    metrics: state.metrics,
    
    // Actions
    sendMessage,
    stopGeneration,
    clearMessages,
    submitFeedback,
    retryMessage,
    
    // Derived state
    hasMessages: state.messages.length > 0,
    lastMessage: state.messages[state.messages.length - 1] || null,
    isHealthy: state.error === null,
  };
}

// Utility functions for formatting
export const formatCitation = (citation: Citation): string => {
  const parts = [citation.title];
  if (citation.page_number) parts.push(`p. ${citation.page_number}`);
  if (citation.source_link) parts.push('View Source');
  return parts.join(' • ');
};

export const formatTokenUsage = (tokenUsage: { prompt_tokens: number; completion_tokens: number; total_tokens: number }) => {
  return `${tokenUsage.total_tokens} tokens (${tokenUsage.prompt_tokens} prompt, ${tokenUsage.completion_tokens} completion)`;
};

export const formatLatency = (ms: number): string => {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
};

export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return 'text-green-600';
  if (confidence >= 0.6) return 'text-yellow-600';
  return 'text-red-600';
};

export const getSafetyIcon = (safetyPassed: boolean, safetyReason?: string) => {
  if (safetyPassed) return '🛡️';
  if (safetyReason?.includes('blocked')) return '🚫';
  return '⚠️';
};
