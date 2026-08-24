import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import type { Wallet } from '../types';
import { getMyWallet } from './wallet.service';

describe('wallet.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('reads only the authenticated wallet contract', async () => {
    const contract: Wallet = {
      id: 'wallet-1',
      user_id: 'user-1',
      balance: '31.50',
      pending_withdrawal: '0.00',
    };
    mock.onGet('/wallets/me').reply(200, contract);

    const response = await getMyWallet();
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<Wallet>();
  });
});
