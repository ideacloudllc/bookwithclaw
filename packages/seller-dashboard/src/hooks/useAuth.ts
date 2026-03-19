import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { setAuthToken, clearAuthToken, getAuthToken } from '../utils/auth';
import { sellers } from '../utils/api';

export const useAuth = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const signup = useCallback(
    async (email: string, password: string, hotel_name: string) => {
      setLoading(true);
      setError(null);
      try {
        const response = await sellers.register({ email, password, hotel_name }) as any;
        if (response?.access_token) {
          setAuthToken(response.access_token);
          navigate('/sellers/portal');
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
        const response = await sellers.login({ email, password }) as any;
        if (response?.access_token) {
          setAuthToken(response.access_token);
          navigate('/sellers/portal');
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
    navigate('/sellers/login');
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
