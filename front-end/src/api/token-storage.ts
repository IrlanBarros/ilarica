const ACCESS_TOKEN_STORAGE_KEY = 'ilarica:access_token';

export const tokenStorage = {
  get(): string | null {
    if (typeof window === 'undefined') {
      return null;
    }

    return window.localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
  },

  set(token: string): void {
    if (typeof window === 'undefined') {
      return;
    }

    window.localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, token);
  },

  clear(): void {
    if (typeof window === 'undefined') {
      return;
    }

    window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
  },

  key: ACCESS_TOKEN_STORAGE_KEY,
};