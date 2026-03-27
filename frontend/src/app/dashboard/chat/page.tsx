'use client';

import { useState } from 'react';

import { LoadingButton } from '@mui/lab';
import { Box, Chip, Paper, Container, TextField, Typography } from '@mui/material';

import { useChat } from 'src/hooks/useChat';

import { DashboardContent } from 'src/layouts/dashboard';

import { useAuthContext } from 'src/auth/hooks';

// ----------------------------------------------------------------------

// Function to parse and render citations from text
const renderTextWithCitations = (text: string) => {
  const citationRegex = /\[Source: ([^,]+), Page: ([^,]+), Clause: ([^\]]+)\]/g;
  
  const parts = [];
  let lastIndex = 0;
  let match;
  
  while ((match = citationRegex.exec(text)) !== null) {
    // Add text before the citation
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    
    // Add the citation as a highlighted chip
    parts.push(
      <Chip
        key={`${match.index}-${match[1]}-${match[2]}`}
        label={`📄 ${match[1]} 📖 ${match[2]} 🏷️ ${match[3]}`}
        variant="outlined"
        size="small"
        sx={{
          mx: 0.5,
          my: 0.5,
          bgcolor: 'primary.light',
          color: 'primary.contrastText',
          fontWeight: 'bold',
          fontSize: '0.75rem'
        }}
      />
    );
    
    lastIndex = citationRegex.lastIndex;
  }
  
  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }
  
  return parts;
};

export default function ChatPage() {
  const { user } = useAuthContext();
  const { loading, error, response, streamingText, askQuestion } = useChat();
  const [message, setMessage] = useState('');
  const [documentId, setDocumentId] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    try {
      await askQuestion({
        message: message.trim(),
        document_id: documentId || undefined
      });
      setMessage('');
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  if (!user) {
    return (
      <DashboardContent>
        <Container maxWidth="md">
          <Typography variant="h4" sx={{ mb: 3, textAlign: 'center' }}>
            Please sign in to use the chat feature.
          </Typography>
        </Container>
      </DashboardContent>
    );
  }

  return (
    <DashboardContent>
      <Container maxWidth="md">
        <Typography variant="h4" sx={{ mb: 3 }}>
          Legal RAG Assistant
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            multiline
            rows={3}
            placeholder="Ask a legal question..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            disabled={loading}
            sx={{ mb: 2 }}
          />
          
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              size="small"
              placeholder="Document ID (optional)"
              value={documentId}
              onChange={(e) => setDocumentId(e.target.value)}
              disabled={loading}
            />
            <LoadingButton
              variant="contained"
              onClick={handleSubmit}
              loading={loading}
              disabled={!message.trim()}
            >
              Ask
            </LoadingButton>
          </Box>
        </Box>

        {error && (
          <Paper sx={{ p: 2, mt: 2, bgcolor: 'error.light', color: 'error.contrastText' }}>
            <Typography variant="body2" color="error">
              Error: {error}
            </Typography>
          </Paper>
        )}

        {(streamingText || response) && (
          <Paper sx={{ p: 3, mt: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Answer:
            </Typography>
            <Box sx={{ 
              whiteSpace: 'pre-wrap', 
              minHeight: '60px',
              '& > *': { display: 'inline-block', mr: 0.5 }
            }}>
              {renderTextWithCitations(streamingText || (response?.answer || ''))}
            </Box>
            
            {response?.citations && response.citations.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  📚 Citations:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {response.citations.map((citation, index) => (
                    <Paper
                      key={index}
                      sx={{
                        p: 1,
                        bgcolor: 'grey.50',
                        border: '1px solid',
                        borderColor: 'grey.300',
                        borderRadius: 1,
                        minWidth: '200px'
                      }}
                    >
                      <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block' }}>
                        📄 {citation.source}
                      </Typography>
                      <Typography variant="caption" sx={{ display: 'block' }}>
                        📖 Page {citation.page}
                      </Typography>
                      <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary' }}>
                        🏷️ {citation.clause}
                      </Typography>
                    </Paper>
                  ))}
                </Box>
              </Box>
            )}
            
            <Typography variant="caption" sx={{ mt: 2, display: 'block', color: 'text.secondary' }}>
              📊 Data points analyzed: {response?.data_points_analyzed || 0}
            </Typography>
          </Paper>
        )}
      </Container>
    </DashboardContent>
  );
}


