const API_BASE = '/api';

export const getAuthToken = (): string | null => {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('buyer_token='))
    ?.split('=')[1] || null;
};

export const apiCall = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith('/') ? endpoint : `${API_BASE}/${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
};

export const buyers = {
  register: (data: { email: string; password: string; name: string }) =>
    apiCall('/api/buyers/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; password: string }) =>
    apiCall('/api/buyers/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  profile: {
    get: () => apiCall('/api/buyers/profile'),
    update: (data: Partial<{
      name: string;
      phone: string;
    }>) =>
      apiCall('/api/buyers/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
  },

  search: {
    list: (params: {
      check_in: string;
      check_out: string;
      occupancy: number;
      room_type?: string;
    }) => {
      const queryParams = new URLSearchParams({
        check_in: params.check_in,
        check_out: params.check_out,
        occupancy: params.occupancy.toString(),
        ...(params.room_type && { room_type: params.room_type }),
      });
      return apiCall(`/api/buyers/search?${queryParams.toString()}`);
    },
  },

  offers: {
    create: (data: {
      room_id: string;
      offered_price: number;
    }) =>
      apiCall('/api/buyers/offers', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    list: () => apiCall('/api/buyers/offers'),
    get: (id: string) => apiCall(`/api/buyers/offers/${id}`),
  },

  negotiations: {
    list: () => apiCall('/api/buyers/negotiations'),
    get: (id: string) => apiCall(`/api/buyers/negotiations/${id}`),
    counter: (id: string, data: { counter_price: number }) =>
      apiCall(`/api/buyers/negotiations/${id}/counter`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    accept: (id: string) =>
      apiCall(`/api/buyers/negotiations/${id}/accept`, {
        method: 'POST',
      }),
    reject: (id: string) =>
      apiCall(`/api/buyers/negotiations/${id}/reject`, {
        method: 'POST',
      }),
    walkaway: (id: string) =>
      apiCall(`/api/buyers/negotiations/${id}/walkaway`, {
        method: 'POST',
      }),
  },

  bookings: {
    list: () => apiCall('/api/buyers/bookings'),
    get: (id: string) => apiCall(`/api/buyers/bookings/${id}`),
  },
};
