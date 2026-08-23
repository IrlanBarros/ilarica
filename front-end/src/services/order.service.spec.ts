import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import {
  createOrder,
  deleteOrder,
  getOrder,
  listOrders,
  updateOrder,
} from './order.service';
import type { ApiMessageResponse, Order, OrderCreate, OrderUpdate } from '../types';

describe('order.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('lists orders with the Order contract', async () => {
    const contract: Order[] = [
      {
        id: 'order-1',
        customer_id: 'user-1',
        canteen_id: 'canteen-1',
        drop_off_zone_id: 'zone-1',
        status: 'draft',
        total_amount: '12.50',
        items: [],
        pickup_pin: null,
      },
    ];

    mock.onGet('/orders/').reply(200, contract);

    const response = await listOrders();

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<Order[]>();
  });

  it('creates an order successfully', async () => {
    const payload: OrderCreate = {
      customer_id: 'user-1',
      canteen_id: 'canteen-1',
      drop_off_zone_id: 'zone-1',
      items: [
        {
          product_id: 'product-1',
          quantity: 2,
          unit_price: '12.50',
        },
      ],
      status: 'draft',
      total_amount: '25.00',
    };

    const contract: Order = {
      id: 'order-1',
      customer_id: 'user-1',
      canteen_id: 'canteen-1',
      drop_off_zone_id: 'zone-1',
      status: 'draft',
      total_amount: '25.00',
      items: [
        {
          id: 'item-1',
          product_id: 'product-1',
          quantity: 2,
          unit_price: '12.50',
        },
      ],
      pickup_pin: null,
    };

    mock.onPost('/orders/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [201, contract];
    });

    const response = await createOrder(payload);

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<Order>();
  });

  it('updates an order successfully', async () => {
    const payload: OrderUpdate = {
      status: 'ready_for_pickup',
      pickup_pin: '1234',
    };

    const contract: Order = {
      id: 'order-1',
      customer_id: 'user-1',
      canteen_id: 'canteen-1',
      drop_off_zone_id: 'zone-1',
      status: 'ready_for_pickup',
      total_amount: '25.00',
      items: [],
      pickup_pin: '1234',
    };

    mock.onPatch('/orders/order-1').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [200, contract];
    });

    const response = await updateOrder('order-1', payload);

    expect(response).toEqual(contract);
  });

  it('returns a normalized error when fetching a missing order', async () => {
    mock.onGet('/orders/missing-order').reply(404, { detail: 'Order not found' });

    await expect(getOrder('missing-order')).rejects.toMatchObject({
      status: 404,
      message: 'Order not found',
      details: 'Order not found',
    });
  });

  it('deletes an order and returns the API message contract', async () => {
    const contract: ApiMessageResponse = {
      detail: 'Order deleted successfully',
    };

    mock.onDelete('/orders/order-1').reply(200, contract);

    const response = await deleteOrder('order-1');

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<ApiMessageResponse>();
  });
});