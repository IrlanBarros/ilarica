import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { redirectToLoginMock } = vi.hoisted(() => ({
  redirectToLoginMock: vi.fn(),
}));

vi.mock('./navigation', () => ({
  redirectToLogin: redirectToLoginMock,
}));

import { apiClient } from './axios.config';
import { ApiClientError } from './http-error';
import { tokenStorage } from './token-storage';

function readHeader(headers: unknown, headerName: string): string | null {
  if (headers && typeof headers === 'object' && 'get' in headers && typeof headers.get === 'function') {
    const value = headers.get(headerName);
    return typeof value === 'string' ? value : null;
  }

  if (headers && typeof headers === 'object' && headerName in headers) {
    const value = (headers as Record<string, unknown>)[headerName];
    return typeof value === 'string' ? value : null;
  }

  return null;
}

describe('apiClient interceptors', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    redirectToLoginMock.mockReset();
  });

  it('injects the bearer token into the Authorization header when a token exists', async () => {
    tokenStorage.set('jwt-token');

    mock.onGet('/secure-resource').reply((config) => {
      expect(readHeader(config.headers, 'Authorization')).toBe('Bearer jwt-token');
      return [200, { ok: true }];
    });

    const response = await apiClient.get<{ ok: boolean }>('/secure-resource');

    expect(response.data).toEqual({ ok: true });
  });

  it('does not inject the Authorization header when no token exists', async () => {
    mock.onGet('/public-resource').reply((config) => {
      expect(readHeader(config.headers, 'Authorization')).toBeNull();
      return [200, { ok: true }];
    });

    const response = await apiClient.get<{ ok: boolean }>('/public-resource');

    expect(response.data).toEqual({ ok: true });
  });

  it('clears auth data and redirects to /login on 401 responses', async () => {
    tokenStorage.set('expired-token');
    window.history.replaceState({}, '', '/dashboard');

    mock.onGet('/protected-resource').reply(401, { detail: 'Could not validate credentials' });

    const request = apiClient.get('/protected-resource');

    await expect(request).rejects.toBeInstanceOf(ApiClientError);
    await expect(request).rejects.toMatchObject({
      status: 401,
      message: 'Could not validate credentials',
    });

    expect(tokenStorage.get()).toBeNull();
    expect(redirectToLoginMock).toHaveBeenCalledTimes(1);
  });
});