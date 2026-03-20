import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { setAuthToken, clearAuthToken, getAuthToken } from '../utils/auth';
import { buyers } from '../utils/api';

export const useAuth = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const signup = useCallback(
    async (email: string, password: string, name: string) => {
      setLoading(true);
      setError(null);
      try {
        const response = await buyers.register({ email, password, name }) as any;
        if (response?.access_token) {
          setAuthToken(response.access_token);
          navigate('/portal');
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Signup failed';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [navigate]
  );

  const login = useCallback(
    async (email: string, password: string) => {
      setLoading(true);
      setError(null);
      try {
        const response = await buyers.login({ email, password }) as any;
        if (response?.access_token) {
          setAuthToken(response.access_token);
          navigate('/portal');
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Login failed';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [navigate]
  );

  const logout = useCallback(() => {
    clearAuthToken();
    // Use hard redirect for logout to ensure clean state reset
    window.location.href = '/buyers/login';
  }, [navigate]);

  const isAuthenticated = !!getAuthToken();

  return {
    signup,
    login,
    logout,
    isAuthenticated,
    loading,
    error,
  };
};
