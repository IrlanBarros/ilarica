import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import type { PaymentTransaction } from '../types';
import { createPaymentTransaction, getPaymentTransaction, listPaymentTransactions } from './payment-transaction.service';

const transaction: PaymentTransaction = {
  id: 'tx-1',
  order_id: 'order-1',
  amount: '18.00',
  payment_method: 'pix',
  status: 'pending',
  external_reference: 'pix-1',
  pix_copy_paste: 'pix-code',
  pix_qr_code: 'data:image/svg+xml;base64,abc',
  expires_at: '2026-08-24T15:00:00Z',
  failure_reason: null,
  created_at: '2026-08-24T14:45:00Z',
  confirmed_at: null,
};

describe('payment-transaction.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('lists only transactions returned for the authenticated user', async () => {
    mock.onGet('/payment-transactions/').reply(200, [transaction]);
    const response = await listPaymentTransactions();
    expect(response).toEqual([transaction]);
    expectTypeOf(response).toEqualTypeOf<PaymentTransaction[]>();
  });

  it('creates an intent with an idempotency key and no client-controlled amount or status', async () => {
    mock.onPost('/payment-transactions/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual({ order_id: 'order-1', payment_method: 'pix' });
      expect(config.headers?.['Idempotency-Key']).toBe('idempotency-key-123456');
      return [201, transaction];
    });

    const response = await createPaymentTransaction(
      { order_id: 'order-1', payment_method: 'pix' },
      'idempotency-key-123456',
    );
    expect(response).toEqual(transaction);
  });

  it('gets the latest transaction state for polling', async () => {
    mock.onGet('/payment-transactions/tx-1').reply(200, { ...transaction, status: 'succeeded' });
    const response = await getPaymentTransaction('tx-1');
    expect(response.status).toBe('succeeded');
  });
});
