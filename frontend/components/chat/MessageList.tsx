/**
 * MessageList Component - Displays chat messages with citations and metrics
 */

import React from 'react';
import { ChatMessage, formatCitation, formatTokenUsage, formatLatency, getConfidenceColor, getSafetyIcon } from '../../hooks/useChat';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onRetryMessage?: (messageId: string) => void;
  onSubmitFeedback?: (messageId: string, rating: number, feedbackType: string, comment?: string) => void;
}

const MessageList: React.FC<MessageListProps> = ({ 
  messages, 
  isLoading, 
  onRetryMessage, 
  onSubmitFeedback 
}) => {
  const [expandedCitations, setExpandedCitations] = React.useState<Set<string>>(new Set());
  const [feedbackStates, setFeedbackStates] = React.useState<Record<string, { rating: number; comment: string }>>({});

  const toggleCitation = (citationId: string) => {
    setExpandedCitations(prev => {
      const newSet = new Set(prev);
      if (newSet.has(citationId)) {
        newSet.delete(citationId);
      } else {
        newSet.add(citationId);
      }
      return newSet;
    });
  };

  const handleSubmitFeedback = (messageId: string) => {
    const feedback = feedbackStates[messageId];
    if (feedback && onSubmitFeedback) {
      onSubmitFeedback(messageId, feedback.rating, 'user_feedback', feedback.comment);
    }
  };

  return (
    <div className="flex flex-col space-y-4 p-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-3xl rounded-lg p-4 ${
              message.role === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-900 border border-gray-200'
            }`}
          >
            {/* Message Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="font-semibold">
                  {message.role === 'user' ? 'You' : 'AI Assistant'}
                </span>
                {message.role === 'assistant' && (
                  <span className="text-sm opacity-75">
                    {getSafetyIcon(message.safety_passed || true, message.safety_reason)}
                  </span>
                )}
              </div>
              <span className="text-xs opacity-75">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>

            {/* Message Content */}
            <div className="prose prose-sm max-w-none">
              {message.content.split('\n').map((paragraph, index) => (
                <p key={index} className="mb-2">
                  {paragraph}
                </p>
              ))}
            </div>

            {/* Citations */}
            {message.citations && message.citations.length > 0 && (
              <div className="mt-4 border-t pt-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-sm">Sources ({message.citations.length})</h4>
                  <button
                    onClick={() => setExpandedCitations(new Set())}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    Collapse All
                  </button>
                </div>
                <div className="space-y-2">
                  {message.citations.map((citation, index) => (
                    <div
                      key={`${citation.source_id}-${index}`}
                      className="bg-white p-3 rounded border border-gray-200 text-sm"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">
                            [Source {index + 1}] {citation.title}
                          </div>
                          <div className="text-xs text-gray-600 mt-1">
                            {formatCitation(citation)}
                          </div>
                          <div className="flex items-center space-x-4 mt-2 text-xs">
                            <span className="text-gray-500">
                              Relevance: {(citation.relevance_score * 100).toFixed(1)}%
                            </span>
                            <span className="text-gray-500">
                              Confidence: {(citation.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                          {citation.quote_snippet && (
                            <div className="mt-2 p-2 bg-gray-50 rounded text-xs italic">
                              "{citation.quote_snippet}"
                            </div>
                          )}
                        </div>
                        <div className="flex flex-col space-y-1">
                          {citation.source_link && (
                            <a
                              href={citation.source_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 text-xs"
                            >
                              View
                            </a>
                          )}
                          <button
                            onClick={() => toggleCitation(`${citation.source_id}-${index}`)}
                            className="text-xs text-gray-600 hover:text-gray-800"
                          >
                            {expandedCitations.has(`${citation.source_id}-${index}`) ? 'Hide' : 'More'}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Metrics and Controls */}
            {message.role === 'assistant' && (
              <div className="mt-4 border-t pt-4">
                <div className="flex items-center justify-between text-xs text-gray-600">
                  <div className="flex items-center space-x-4">
                    {message.confidence_score !== undefined && (
                      <span className={getConfidenceColor(message.confidence_score)}>
                        Confidence: {(message.confidence_score * 100).toFixed(1)}%
                      </span>
                    )}
                    {message.generation_time && (
                      <span>Latency: {formatLatency(message.generation_time * 1000)}</span>
                    )}
                    {message.token_usage && (
                      <span>{formatTokenUsage(message.token_usage)}</span>
                    )}
                    {message.model_used && (
                      <span>Model: {message.model_used}</span>
                    )}
                  </div>
                  {!message.safety_passed && (
                    <span className="text-red-600 font-medium">
                      {message.safety_reason || 'Content filtered'}
                    </span>
                  )}
                </div>

                {/* Follow-up Questions */}
                {message.follow_up_questions && message.follow_up_questions.length > 0 && (
                  <div className="mt-3">
                    <h5 className="font-medium text-sm mb-2">Follow-up Questions:</h5>
                    <div className="space-y-1">
                      {message.follow_up_questions.map((question, index) => (
                        <div
                          key={index}
                          className="text-xs bg-blue-50 text-blue-800 p-2 rounded cursor-pointer hover:bg-blue-100"
                          onClick={() => {
                            // This would trigger sending the follow-up question
                            console.log('Follow-up question:', question);
                          }}
                        >
                          {question}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Feedback Controls */}
                {onSubmitFeedback && (
                  <div className="mt-3 pt-3 border-t">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-medium">Rate this response:</span>
                      {[1, 2, 3, 4, 5].map((rating) => (
                        <button
                          key={rating}
                          onClick={() => {
                            setFeedbackStates(prev => ({
                              ...prev,
                              [message.id]: { ...prev[message.id], rating }
                            }));
                          }}
                          className={`text-lg ${
                            feedbackStates[message.id]?.rating >= rating
                              ? 'text-yellow-500'
                              : 'text-gray-300'
                          }`}
                        >
                          ★
                        </button>
                      ))}
                      <textarea
                        placeholder="Add comment (optional)"
                        className="text-xs p-1 border rounded"
                        value={feedbackStates[message.id]?.comment || ''}
                        onChange={(e) => {
                          setFeedbackStates(prev => ({
                            ...prev,
                            [message.id]: { ...prev[message.id], comment: e.target.value }
                          }));
                        }}
                      />
                      <button
                        onClick={() => handleSubmitFeedback(message.id)}
                        className="text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                      >
                        Submit
                      </button>
                    </div>
                  </div>
                )}

                {/* Retry Button for Failed Messages */}
                {!message.safety_passed && onRetryMessage && (
                  <div className="mt-2">
                    <button
                      onClick={() => onRetryMessage(message.id)}
                      className="text-xs bg-gray-500 text-white px-2 py-1 rounded hover:bg-gray-600"
                    >
                      Retry
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Loading Indicator */}
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 rounded-lg p-4 border border-gray-200">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span className="text-sm text-gray-600">AI is thinking...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageList;
