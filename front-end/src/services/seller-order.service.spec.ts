import MockAdapter from 'axios-mock-adapter';
import { afterEach, describe, expect, it } from 'vitest';

import { apiClient } from '../api';
import { listSellerOrderHistory, listSellerOrders, updateSellerOrderStatus } from './seller-order.service';

const mock = new MockAdapter(apiClient);

afterEach(() => mock.reset());

describe('seller order service', () => {
  it('uses the authenticated canteen-scoped collection', async () => {
    mock.onGet('/canteens/me/orders').reply(200, []);
    await expect(listSellerOrders()).resolves.toEqual([]);
  });

  it('uses the authenticated canteen-scoped completed history', async () => {
    mock.onGet('/canteens/me/orders/history').reply(200, []);
    await expect(listSellerOrderHistory()).resolves.toEqual([]);
  });

  it('sends only the explicit next status', async () => {
    const response = { id: 'order-id', status: 'preparing' };
    mock.onPatch('/canteens/me/orders/order-id/status', { status: 'preparing' }).reply(200, response);
    await expect(updateSellerOrderStatus('order-id', { status: 'preparing' })).resolves.toEqual(response);
  });
});
