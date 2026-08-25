import { describe, expect, it } from 'vitest';

import type { CartItem } from '../store/useCartStore';
import { buildOrderPayload } from './build-order-payload';

const items: CartItem[] = [
  {
    product: {
      id: 'product-1',
      canteen_id: 'canteen-1',
      name: 'Coxinha',
      description: null,
      price: '6.5',
      is_active: true,
      is_fast_stock_enabled: false,
    },
    quantity: 2,
  },
];

describe('buildOrderPayload', () => {
  it('builds only the exact fields required by POST /orders', () => {
    expect(
      buildOrderPayload({
        customerId: 'customer-1',
        canteenId: 'canteen-1',
        dropOffZoneId: 'zone-1',
        items,
      }),
    ).toEqual({
      customer_id: 'customer-1',
      canteen_id: 'canteen-1',
      fulfillment_type: 'delivery',
      drop_off_zone_id: 'zone-1',
      items: [{ product_id: 'product-1', quantity: 2 }],
    });
  });

  it('rejects empty carts and mixed canteens', () => {
    expect(() =>
      buildOrderPayload({
        customerId: 'customer-1',
        canteenId: 'canteen-1',
        dropOffZoneId: 'zone-1',
        items: [],
      }),
    ).toThrow('At least one cart item');

    expect(() =>
      buildOrderPayload({
        customerId: 'customer-1',
        canteenId: 'canteen-2',
        dropOffZoneId: 'zone-1',
        items,
      }),
    ).toThrow('selected canteen');
  });
});
