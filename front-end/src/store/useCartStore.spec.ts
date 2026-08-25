import { beforeEach, describe, expect, it } from 'vitest';

import type { Product } from '../types';
import { CartCanteenConflictError, useCartStore } from './useCartStore';

const product: Product = {
  id: 'product-1',
  canteen_id: 'canteen-1',
  name: 'Coxinha',
  description: null,
  price: '6.50',
  is_active: true,
  is_fast_stock_enabled: false,
  category: 'salgados',
  stock_quantity: 20,
};

describe('useCartStore', () => {
  beforeEach(() => {
    useCartStore.getState().clearCart();
    window.localStorage.clear();
  });

  it('recalculates totals for add, update and remove operations', () => {
    useCartStore.getState().addItem(product, 2);
    expect(useCartStore.getState().total).toBe(13);

    useCartStore.getState().updateQuantity(product.id, 3);
    expect(useCartStore.getState().total).toBe(19.5);

    useCartStore.getState().removeItem(product.id);
    expect(useCartStore.getState()).toMatchObject({ items: [], canteenId: null, total: 0 });
  });

  it('blocks mixing canteens and supports an explicit conscious replacement', () => {
    const otherProduct = { ...product, id: 'product-2', canteen_id: 'canteen-2' };
    useCartStore.getState().addItem(product);

    expect(() => useCartStore.getState().addItem(otherProduct)).toThrow(CartCanteenConflictError);
    expect(useCartStore.getState().canteenId).toBe('canteen-1');

    useCartStore.getState().replaceCart(otherProduct, 2);
    expect(useCartStore.getState().items).toEqual([{ product: otherProduct, quantity: 2 }]);
    expect(useCartStore.getState().canteenId).toBe('canteen-2');
  });

  it('persists the cart and safely recomputes derived state during rehydration', async () => {
    useCartStore.getState().addItem(product, 2);
    const persisted = window.localStorage.getItem('ilarica-cart');
    expect(persisted).toContain('product-1');

    useCartStore.setState({ items: [], canteenId: null, total: 0 });
    window.localStorage.setItem('ilarica-cart', persisted!);
    await useCartStore.persist.rehydrate();

    expect(useCartStore.getState().items[0].quantity).toBe(2);
    expect(useCartStore.getState().canteenId).toBe('canteen-1');
    expect(useCartStore.getState().total).toBe(13);
  });
});
