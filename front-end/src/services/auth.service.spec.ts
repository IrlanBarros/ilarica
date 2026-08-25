import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it, vi } from 'vitest';

const { redirectToLoginMock } = vi.hoisted(() => ({
  redirectToLoginMock: vi.fn(),
}));

vi.mock('../api/navigation', () => ({
  redirectToLogin: redirectToLoginMock,
}));

import { apiClient } from '../api';
import { tokenStorage } from '../api/token-storage';
import {
  confirmEmailVerification,
  login,
  logout,
  register,
  requestEmailVerification,
} from './auth.service';
import type { LoginRequest, TokenResponse, User, UserCreate, ValidationErrorDetail } from '../types';

describe('auth.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    redirectToLoginMock.mockReset();
  });

  it('logs in successfully and returns a typed token response', async () => {
    const payload: LoginRequest = {
      username: 'auth.success@ufca.edu.br',
      password: 'Secret123',
      grant_type: 'password',
    };

    const contract: TokenResponse = {
      access_token: 'jwt-token',
      token_type: 'bearer',
    };

    mock.onPost('/auth/login').reply((config) => {
      expect(String(config.data)).toContain('username=auth.success%40ufca.edu.br');
      expect(String(config.data)).toContain('password=Secret123');
      expect(String(config.data)).toContain('grant_type=password');
      return [200, contract];
    });

    const response = await login(payload);

    expect(response).toEqual(contract);
    expect(tokenStorage.get()).toBe('jwt-token');
    expectTypeOf(response).toEqualTypeOf<TokenResponse>();
  });

  it('normalizes login validation failures', async () => {
    const details: ValidationErrorDetail[] = [
      {
        loc: ['body', 'username'],
        msg: 'Field required',
        type: 'missing',
      },
    ];

    mock.onPost('/auth/login').reply(422, { detail: details });

    await expect(
      login({
        username: 'invalid@ufca.edu.br',
        password: 'Secret123',
      }),
    ).rejects.toMatchObject({
      status: 422,
      details,
    });
  });

  it('registers a user successfully and returns a typed user contract', async () => {
    const payload: UserCreate = {
      name: 'Test User',
      email: 'testuser@ufca.edu.br',
      whatsapp: '5588999999999',
      password: 'Secret123',
      role: 'customer',
    };

    const contract: User = {
      id: 'user-1',
      name: 'Test User',
      email: 'testuser@ufca.edu.br',
      whatsapp: '5588999999999',
      role: 'customer',
      is_active: true,
      is_email_validated: false,
    };

    mock.onPost('/users/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [201, contract];
    });

    const response = await register(payload);

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<User>();
  });

  it('normalizes register business-rule failures', async () => {
    mock.onPost('/users/').reply(400, { detail: 'Role is not valid for the platform.' });

    await expect(
      register({
        name: 'Broken User',
        email: 'broken@ufca.edu.br',
        whatsapp: '5588999999998',
        password: 'Secret123',
        role: 'courier',
      }),
    ).rejects.toMatchObject({
      status: 400,
      message: 'Role is not valid for the platform.',
      details: 'Role is not valid for the platform.',
    });
  });

  it('clears local auth data and redirects during logout', () => {
    tokenStorage.set('jwt-token');

    logout();

    expect(tokenStorage.get()).toBeNull();
    expect(redirectToLoginMock).toHaveBeenCalledTimes(1);
  });

  it('requests and confirms institutional email verification', async () => {
    mock.onPost('/auth/email-verification/request', { email: 'user@ufca.edu.br' }).reply(202);
    mock.onPost('/auth/email-verification/confirm', { token: 'secure-token' }).reply(200);

    await expect(requestEmailVerification('user@ufca.edu.br')).resolves.toBeUndefined();
    await expect(confirmEmailVerification('secure-token')).resolves.toBeUndefined();
  });
});
