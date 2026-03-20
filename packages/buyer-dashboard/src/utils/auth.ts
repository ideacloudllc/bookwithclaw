export const setAuthToken = (token: string): void => {
  document.cookie = `buyer_token=${token}; path=/; max-age=${30 * 24 * 60 * 60}; SameSite=Lax`;
};

export const clearAuthToken = (): void => {
  document.cookie = 'buyer_token=; path=/; max-age=0';
};

export const getAuthToken = (): string | null => {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('buyer_token='))
    ?.split('=')[1] || null;
};

export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};

export const validateEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password: string): boolean => {
  return password.length >= 8;
};

export const validateName = (name: string): boolean => {
  return name.trim().length >= 2;
};
