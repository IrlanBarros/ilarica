import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import {
  createWallet,
  deleteWallet,
  getWallet,
  listWallets,
  updateWallet,
} from './wallet.service';
import type { ApiMessageResponse, Wallet, WalletCreate, WalletUpdate } from '../types';

describe('wallet.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('lists wallets with the Wallet contract', async () => {
    const contract: Wallet[] = [
      {
        id: 'wallet-1',
        user_id: 'user-1',
        balance: '10.25',
        pending_withdrawal: '0.00',
      },
    ];

    mock.onGet('/wallets/').reply(200, contract);

    const response = await listWallets();

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<Wallet[]>();
  });

  it('creates a wallet successfully', async () => {
    const payload: WalletCreate = {
      user_id: 'user-1',
      balance: '20.00',
      pending_withdrawal: '0.00',
    };

    const contract: Wallet = {
      id: 'wallet-1',
      user_id: 'user-1',
      balance: '20.00',
      pending_withdrawal: '0.00',
    };

    mock.onPost('/wallets/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [201, contract];
    });

    const response = await createWallet(payload);

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<Wallet>();
  });

  it('updates a wallet successfully', async () => {
    const payload: WalletUpdate = {
      balance: '35.00',
    };

    const contract: Wallet = {
      id: 'wallet-1',
      user_id: 'user-1',
      balance: '35.00',
      pending_withdrawal: '0.00',
    };

    mock.onPatch('/wallets/wallet-1').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [200, contract];
    });

    const response = await updateWallet('wallet-1', payload);

    expect(response).toEqual(contract);
  });

  it('returns a normalized error when fetching a missing wallet', async () => {
    mock.onGet('/wallets/missing-wallet').reply(404, { detail: 'Wallet not found' });

    await expect(getWallet('missing-wallet')).rejects.toMatchObject({
      status: 404,
      message: 'Wallet not found',
      details: 'Wallet not found',
    });
  });

  it('deletes a wallet and returns the API message contract', async () => {
    const contract: ApiMessageResponse = {
      detail: 'Wallet deleted successfully',
    };

    mock.onDelete('/wallets/wallet-1').reply(200, contract);

    const response = await deleteWallet('wallet-1');

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<ApiMessageResponse>();
  });
});