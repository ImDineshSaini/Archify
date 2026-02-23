import { useState, useCallback } from 'react';

/**
 * Shared hook for API calls with loading/error/success state management.
 * Handles 403 automatically and reduces boilerplate in Settings/Repositories.
 */
export default function useApiCall() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const clearMessages = useCallback(() => {
    setError('');
    setSuccess('');
  }, []);

  const execute = useCallback(async (apiCall, options = {}) => {
    const { successMessage, onSuccess, onError } = options;
    setLoading(true);
    clearMessages();

    try {
      const result = await apiCall();
      if (successMessage) setSuccess(successMessage);
      if (onSuccess) onSuccess(result);
      return result;
    } catch (err) {
      const message =
        err.response?.status === 403
          ? 'Access denied. Admin privileges required.'
          : err.response?.data?.detail || err.message || 'An error occurred';
      setError(message);
      if (onError) onError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [clearMessages]);

  return { loading, error, success, execute, clearMessages, setError, setSuccess };
}
