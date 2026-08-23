import { create } from 'zustand';

import type { Product } from '../types';

export interface CartItem {
  product: Product;
  quantity: number;
}

interface CartState {
  items: CartItem[];
  canteenId: string | null;
  total: number;
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
}

function toMoneyNumber(value: string): number {
  const numericValue = Number.parseFloat(value);
  return Number.isFinite(numericValue) ? numericValue : 0;
}

function calculateTotal(items: CartItem[]): number {
  return items.reduce((acc, item) => acc + toMoneyNumber(item.product.price) * item.quantity, 0);
}

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  canteenId: null,
  total: 0,

  addItem(product: Product, quantity = 1): void {
    if (quantity <= 0) {
      throw new Error('Quantity must be greater than zero.');
    }

    const { items, canteenId } = get();

    if (canteenId !== null && canteenId !== product.canteen_id) {
      throw new Error('Cart contains items from another canteen. Clear cart before adding this product.');
    }

    const existingItem = items.find((item) => item.product.id === product.id);
    let nextItems: CartItem[];

    if (existingItem) {
      nextItems = items.map((item) =>
        item.product.id === product.id
          ? {
              ...item,
              quantity: item.quantity + quantity,
            }
          : item,
      );
    } else {
      nextItems = [...items, { product, quantity }];
    }

    set({
      items: nextItems,
      canteenId: product.canteen_id,
      total: calculateTotal(nextItems),
    });
  },

  removeItem(productId: string): void {
    const { items } = get();
    const nextItems = items.filter((item) => item.product.id !== productId);

    set({
      items: nextItems,
      canteenId: nextItems.length > 0 ? nextItems[0].product.canteen_id : null,
      total: calculateTotal(nextItems),
    });
  },

  updateQuantity(productId: string, quantity: number): void {
    if (quantity <= 0) {
      get().removeItem(productId);
      return;
    }

    const { items } = get();
    const nextItems = items.map((item) =>
      item.product.id === productId
        ? {
            ...item,
            quantity,
          }
        : item,
    );

    set({
      items: nextItems,
      canteenId: nextItems.length > 0 ? nextItems[0].product.canteen_id : null,
      total: calculateTotal(nextItems),
    });
  },

  clearCart(): void {
    set({
      items: [],
      canteenId: null,
      total: 0,
    });
  },
}));