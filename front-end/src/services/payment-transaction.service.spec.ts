import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import type {
  ApiMessageResponse,
  PaymentTransaction,
  PaymentTransactionCreate,
  PaymentTransactionUpdate,
} from '../types';
import {
  createPaymentTransaction,
  deletePaymentTransaction,
  getPaymentTransaction,
  listPaymentTransactions,
  updatePaymentTransaction,
} from './payment-transaction.service';

describe('payment-transaction.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('lists payment transactions with the PaymentTransaction contract', async () => {
    const contract: PaymentTransaction[] = [
      {
        id: 'tx-1',
        order_id: 'order-1',
        amount: '25.00',
        payment_method: 'wallet',
        status: 'pending',
        external_reference: null,
      },
    ];
    mock.onGet('/payment-transactions/').reply(200, contract);
    const response = await listPaymentTransactions();
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<PaymentTransaction[]>();
  });

  it('creates a payment transaction successfully', async () => {
    const payload: PaymentTransactionCreate = {
      order_id: 'order-1',
      amount: '25.00',
      payment_method: 'wallet',
      status: 'pending',
      external_reference: null,
    };
    const contract: PaymentTransaction = {
      id: 'tx-1',
      order_id: 'order-1',
      amount: '25.00',
      payment_method: 'wallet',
      status: 'pending',
      external_reference: null,
    };
    mock.onPost('/payment-transactions/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [201, contract];
    });
    const response = await createPaymentTransaction(payload);
    expect(response).toEqual(contract);
  });

  it('updates a payment transaction successfully', async () => {
    const payload: PaymentTransactionUpdate = { status: 'succeeded', external_reference: 'ext-123' };
    const contract: PaymentTransaction = {
      id: 'tx-1',
      order_id: 'order-1',
      amount: '25.00',
      payment_method: 'wallet',
      status: 'succeeded',
      external_reference: 'ext-123',
    };
    mock.onPatch('/payment-transactions/tx-1').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [200, contract];
    });
    const response = await updatePaymentTransaction('tx-1', payload);
    expect(response).toEqual(contract);
  });

  it('normalizes not-found errors', async () => {
    mock.onGet('/payment-transactions/missing-tx').reply(404, { detail: 'Payment transaction not found' });
    await expect(getPaymentTransaction('missing-tx')).rejects.toMatchObject({
      status: 404,
      message: 'Payment transaction not found',
      details: 'Payment transaction not found',
    });
  });

  it('deletes a payment transaction and returns the API message contract', async () => {
    const contract: ApiMessageResponse = { detail: 'Payment transaction deleted successfully' };
    mock.onDelete('/payment-transactions/tx-1').reply(200, contract);
    const response = await deletePaymentTransaction('tx-1');
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<ApiMessageResponse>();
  });
});