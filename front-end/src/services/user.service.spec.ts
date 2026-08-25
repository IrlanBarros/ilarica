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
import { getMe } from './user.service';
import type { User } from '../types';

describe('user.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    redirectToLoginMock.mockReset();
  });

  it('fetches the authenticated user profile and matches the User contract', async () => {
    const contract: User = {
      id: 'test-auth-user',
      name: 'qa-auth',
      email: 'qa-auth@ufca.edu.br',
      whatsapp: '5588999999999',
      role: 'admin',
      is_active: true,
      is_email_validated: true,
    };

    mock.onGet('/users/me').reply(200, contract);

    const response = await getMe();

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<User>();
  });

  it('normalizes profile fetch failures', async () => {
    mock.onGet('/users/me').reply(404, { detail: 'User not found' });

    await expect(getMe()).rejects.toMatchObject({
      status: 404,
      message: 'User not found',
      details: 'User not found',
    });
  });

  it('handles an invalid boot token by clearing auth state and redirecting to login', async () => {
    tokenStorage.set('expired-token');

    mock.onGet('/users/me').reply(401, { detail: 'Could not validate credentials' });

    await expect(getMe()).rejects.toMatchObject({
      status: 401,
      message: 'Could not validate credentials',
      details: 'Could not validate credentials',
    });

    expect(tokenStorage.get()).toBeNull();
    expect(redirectToLoginMock).toHaveBeenCalledTimes(1);
  });
});
