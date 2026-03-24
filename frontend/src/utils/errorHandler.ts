/**
 * Standardized error handling utilities for consistent error processing across hooks
 */

export interface ErrorHandlerOptions {
  fallbackMessage?: string;
  context?: string;
  logError?: boolean;
}

/**
 * Standardized error handler for consistent error processing
 */
export function handleError(error: unknown, options: ErrorHandlerOptions = {}): string {
  const { fallbackMessage = 'An unexpected error occurred', context = '', logError = true } = options;
  
  let errorMessage = fallbackMessage;
  
  if (error instanceof Error) {
    errorMessage = error.message;
  } else if (typeof error === 'string') {
    errorMessage = error;
  } else if (error && typeof error === 'object' && 'message' in error) {
    errorMessage = (error as any).message || fallbackMessage;
  }
  
  // Add context if provided
  if (context) {
    errorMessage = `${context}: ${errorMessage}`;
  }
  
  // Log error for debugging
  if (logError) {
    console.error('Error occurred:', error);
  }
  
  return errorMessage;
}

/**
 * Standardized async error wrapper for consistent error handling in async operations
 */
export async function withErrorHandling<T>(
  asyncOperation: () => Promise<T>,
  options: ErrorHandlerOptions = {}
): Promise<{ data: T | null; error: string | null }> {
  try {
    const data = await asyncOperation();
    return { data, error: null };
  } catch (error) {
    const errorMessage = handleError(error, options);
    return { data: null, error: errorMessage };
  }
}
