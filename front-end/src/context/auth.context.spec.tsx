import MockAdapter from 'axios-mock-adapter';
import { act, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { redirectToLoginMock } = vi.hoisted(() => ({
  redirectToLoginMock: vi.fn(),
}));

vi.mock('../api/navigation', () => ({
  redirectToLogin: redirectToLoginMock,
}));

import { apiClient, tokenStorage } from '../api';
import { AuthFlowHarness } from '../test/auth-flow-harness';
import { AuthProvider } from './auth.context';

describe('AuthContext integration', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    redirectToLoginMock.mockReset();
  });

  it('hydrates the authenticated user on boot when a valid token is present', async () => {
    tokenStorage.set('valid-token');

    mock.onGet('/users/me').reply(200, {
      id: 'test-auth-user',
      name: 'qa-auth',
      email: 'qa-auth@ufca.edu.br',
      role: 'admin',
      is_active: true,
    });

    render(
      <AuthProvider>
        <AuthFlowHarness />
      </AuthProvider>,
    );

    expect(screen.getByTestId('status').textContent).toBe('loading');

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('authenticated');
    });

    expect(screen.getByTestId('hydrated').textContent).toBe('true');
    expect(screen.getByTestId('authenticated').textContent).toBe('true');
    expect(screen.getByTestId('user-email').textContent).toBe('qa-auth@ufca.edu.br');
  });

  it('stays unauthenticated on boot when no token exists', async () => {
    render(
      <AuthProvider>
        <AuthFlowHarness />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('unauthenticated');
    });

    expect(screen.getByTestId('hydrated').textContent).toBe('true');
    expect(screen.getByTestId('authenticated').textContent).toBe('false');
    expect(screen.getByTestId('user-email').textContent).toBe('anonymous');
  });

  it('auto-logs out during boot when the stored token is invalid', async () => {
    tokenStorage.set('expired-token');

    mock.onGet('/users/me').reply(401, { detail: 'Could not validate credentials' });

    render(
      <AuthProvider>
        <AuthFlowHarness />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('unauthenticated');
    });

    expect(screen.getByTestId('hydrated').textContent).toBe('true');
    expect(screen.getByTestId('authenticated').textContent).toBe('false');
    expect(screen.getByTestId('user-email').textContent).toBe('anonymous');
    expect(tokenStorage.get()).toBeNull();
    expect(redirectToLoginMock).toHaveBeenCalledTimes(1);
  });

  it('clears local auth state when logout is triggered from the context', async () => {
    tokenStorage.set('valid-token');

    mock.onGet('/users/me').reply(200, {
      id: 'test-auth-user',
      name: 'qa-auth',
      email: 'qa-auth@ufca.edu.br',
      role: 'admin',
      is_active: true,
    });

    render(
      <AuthProvider>
        <AuthFlowHarness />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('authenticated');
    });

    await act(async () => {
      screen.getByRole('button', { name: 'logout' }).click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('unauthenticated');
    });

    expect(screen.getByTestId('authenticated').textContent).toBe('false');
    expect(screen.getByTestId('user-email').textContent).toBe('anonymous');
    expect(tokenStorage.get()).toBeNull();
    expect(redirectToLoginMock).toHaveBeenCalledTimes(1);
  });

  it('executes the full login to hydrate to logout flow with a real auth component', async () => {
    mock.onPost('/auth/login').reply((config) => {
      expect(String(config.data)).toContain('username=qa-auth%40ufca.edu.br');
      expect(String(config.data)).toContain('password=Secret123');
      expect(String(config.data)).toContain('grant_type=password');
      return [200, { access_token: 'jwt-token', token_type: 'bearer' }];
    });

    mock.onGet('/users/me').reply(200, {
      id: 'test-auth-user',
      name: 'qa-auth',
      email: 'qa-auth@ufca.edu.br',
      role: 'admin',
      is_active: true,
    });

    render(
      <AuthProvider>
        <AuthFlowHarness />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('unauthenticated');
    });

    await act(async () => {
      screen.getByRole('button', { name: 'login' }).click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('authenticated');
    });

    expect(screen.getByTestId('authenticated').textContent).toBe('true');
    expect(screen.getByTestId('user-email').textContent).toBe('qa-auth@ufca.edu.br');
    expect(tokenStorage.get()).toBe('jwt-token');

    await act(async () => {
      screen.getByRole('button', { name: 'logout' }).click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('unauthenticated');
    });

    expect(screen.getByTestId('authenticated').textContent).toBe('false');
    expect(screen.getByTestId('user-email').textContent).toBe('anonymous');
    expect(tokenStorage.get()).toBeNull();
    expect(redirectToLoginMock).toHaveBeenCalledTimes(1);
  });
});