const API_BASE = '/api';

export const getAuthToken = (): string | null => {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('seller_token='))
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

export const sellers = {
  register: (data: { email: string; password: string; hotel_name: string }) =>
    apiCall('/api/sellers/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; password: string }) =>
    apiCall('/api/sellers/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  profile: {
    get: () => apiCall('/api/sellers/profile'),
    update: (data: Partial<{
      hotel_name: string;
      address: string;
      phone: string;
      check_in_time: string;
      check_out_time: string;
    }>) =>
      apiCall('/api/sellers/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
  },

  rooms: {
    list: () => apiCall('/api/sellers/rooms'),
    create: (data: {
      name: string;
      type: string;
      base_price: number;
      floor_price: number;
      max_occupancy: number;
    }) =>
      apiCall('/api/sellers/rooms', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: any) =>
      apiCall(`/api/sellers/rooms/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiCall(`/api/sellers/rooms/${id}`, {
        method: 'DELETE',
      }),
  },

  offers: {
    list: () => apiCall('/api/sellers/offers'),
    counter: (id: string, data: { counter_price: number }) =>
      apiCall(`/api/sellers/offers/${id}/counter`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    accept: (id: string) =>
      apiCall(`/api/sellers/offers/${id}/accept`, {
        method: 'POST',
      }),
  },

  bookings: {
    list: () => apiCall('/api/sellers/bookings'),
  },
};
