import axios, { AxiosError, AxiosHeaders } from 'axios';

import { normalizeApiError } from './http-error';
import { redirectToLogin } from './navigation';
import { tokenStorage } from './token-storage';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = tokenStorage.get();

    if (!token) {
      return config;
    }

    const headers =
      config.headers instanceof AxiosHeaders ? config.headers : new AxiosHeaders(config.headers);

    headers.set('Authorization', `Bearer ${token}`);
    config.headers = headers;

    return config;
  },
  (error: AxiosError) => Promise.reject(normalizeApiError(error)),
);

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      tokenStorage.clear();
      redirectToLogin();
    }

    return Promise.reject(normalizeApiError(error));
  },
);