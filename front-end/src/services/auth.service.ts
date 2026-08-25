import { apiClient, redirectToLogin, tokenStorage } from '../api';
import type { LoginRequest, TokenResponse, User, UserCreate } from '../types';

function buildLoginFormPayload(payload: LoginRequest): URLSearchParams {
  const formData = new URLSearchParams();

  formData.set('username', payload.username);
  formData.set('password', payload.password);

  if (payload.grant_type) {
    formData.set('grant_type', payload.grant_type);
  }

  if (payload.scope) {
    formData.set('scope', payload.scope);
  }

  if (payload.client_id) {
    formData.set('client_id', payload.client_id);
  }

  if (payload.client_secret) {
    formData.set('client_secret', payload.client_secret);
  }

  return formData;
}

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/login', buildLoginFormPayload(payload), {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  tokenStorage.set(response.data.access_token);

  return response.data;
}

export async function register(payload: UserCreate): Promise<User> {
  const response = await apiClient.post<User>('/users/', payload);

  return response.data;
}

export async function requestPasswordReset(email: string): Promise<void> {
  await apiClient.post('/auth/password-reset/request', { email });
}

export async function confirmPasswordReset(token: string, password: string): Promise<void> {
  await apiClient.post('/auth/password-reset/confirm', { token, password });
}

export async function requestEmailVerification(email: string): Promise<void> {
  await apiClient.post('/auth/email-verification/request', { email });
}

export async function confirmEmailVerification(token: string): Promise<void> {
  await apiClient.post('/auth/email-verification/confirm', { token });
}

export function logout(): void {
  tokenStorage.clear();
  redirectToLogin();
}
