import { useState, useEffect, useCallback } from 'react';
import { apiCall } from '../utils/api';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export const useApi = <T,>(
  endpoint: string,
  deps: any[] = []
): UseApiState<T> & { refetch: () => void } => {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const data = await apiCall<T>(endpoint);
      setState({ data, loading: false, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch data';
      setState({ data: null, loading: false, error: message });
    }
  }, [endpoint]);

  useEffect(() => {
    fetchData();
  }, [endpoint, ...deps]);

  return { ...state, refetch: fetchData };
};
