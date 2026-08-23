import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import type {
  ApiMessageResponse,
  InvitationKey,
  InvitationKeyCreate,
  InvitationKeyUpdate,
} from '../types';
import {
  createInvitationKey,
  deleteInvitationKey,
  getInvitationKey,
  listInvitationKeys,
  updateInvitationKey,
} from './invitation-key.service';

describe('invitation-key.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('lists invitation keys with the InvitationKey contract', async () => {
    const contract: InvitationKey[] = [
      {
        id: 'key-1',
        key: 'INVITE1',
        issued_to_email: '',
        expires_at: '2026-08-20T12:00:00Z',
        is_used: false,
        is_expired: false,
        used_by_user_id: null,
      },
    ];
    mock.onGet('/invitation-keys/').reply(200, contract);
    const response = await listInvitationKeys();
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<InvitationKey[]>();
  });

  it('creates an invitation key successfully', async () => {
    const payload: InvitationKeyCreate = {
      key: 'INVITE1',
      issued_to_email: 'student@ufca.edu.br',
      expires_at: '2026-08-20T12:00:00Z',
      is_used: false,
      is_expired: false,
    };
    const contract: InvitationKey = {
      id: 'key-1',
      key: 'INVITE1',
      issued_to_email: 'student@ufca.edu.br',
      expires_at: '2026-08-20T12:00:00Z',
      is_used: false,
      is_expired: false,
      used_by_user_id: null,
    };
    mock.onPost('/invitation-keys/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [201, contract];
    });
    const response = await createInvitationKey(payload);
    expect(response).toEqual(contract);
  });

  it('updates an invitation key successfully', async () => {
    const payload: InvitationKeyUpdate = { is_used: true, is_expired: true };
    const contract: InvitationKey = {
      id: 'key-1',
      key: 'INVITE1',
      issued_to_email: '',
      expires_at: '2026-08-20T12:00:00Z',
      is_used: true,
      is_expired: true,
      used_by_user_id: null,
    };
    mock.onPatch('/invitation-keys/key-1').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [200, contract];
    });
    const response = await updateInvitationKey('key-1', payload);
    expect(response).toEqual(contract);
  });

  it('normalizes not-found errors', async () => {
    mock.onGet('/invitation-keys/missing-key').reply(404, { detail: 'Invitation key not found' });
    await expect(getInvitationKey('missing-key')).rejects.toMatchObject({
      status: 404,
      message: 'Invitation key not found',
      details: 'Invitation key not found',
    });
  });

  it('deletes an invitation key and returns the API message contract', async () => {
    const contract: ApiMessageResponse = { detail: 'Invitation key deleted successfully' };
    mock.onDelete('/invitation-keys/key-1').reply(200, contract);
    const response = await deleteInvitationKey('key-1');
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<ApiMessageResponse>();
  });
});