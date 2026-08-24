import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import type { Product } from '../types';

export interface CartItem {
  product: Product;
  quantity: number;
}

export class CartCanteenConflictError extends Error {
  constructor() {
    super('Cart contains items from another canteen. Clear or replace the cart before adding this product.');
    this.name = 'CartCanteenConflictError';
  }
}

interface CartState {
  items: CartItem[];
  canteenId: string | null;
  total: number;
  addItem: (product: Product, quantity?: number) => void;
  replaceCart: (product: Product, quantity?: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
}

function toMoneyNumber(value: string): number {
  const numericValue = Number.parseFloat(value);
  return Number.isFinite(numericValue) ? numericValue : 0;
}

export function calculateCartTotal(items: CartItem[]): number {
  return items.reduce((acc, item) => acc + toMoneyNumber(item.product.price) * item.quantity, 0);
}

function isCartItem(value: unknown): value is CartItem {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<CartItem>;
  return (
    Number.isInteger(candidate.quantity) &&
    Number(candidate.quantity) > 0 &&
    Boolean(candidate.product) &&
    typeof candidate.product?.id === 'string' &&
    typeof candidate.product?.canteen_id === 'string' &&
    typeof candidate.product?.name === 'string' &&
    typeof candidate.product?.price === 'string'
  );
}

function sanitizePersistedItems(value: unknown): CartItem[] {
  if (!Array.isArray(value)) return [];
  const validItems = value.filter(isCartItem);
  const firstCanteenId = validItems[0]?.product.canteen_id;
  return firstCanteenId
    ? validItems.filter((item) => item.product.canteen_id === firstCanteenId)
    : [];
}

export const useCartStore = create<CartState>()(persist((set, get) => ({
  items: [],
  canteenId: null,
  total: 0,

  addItem(product: Product, quantity = 1): void {
    if (quantity <= 0) {
      throw new Error('Quantity must be greater than zero.');
    }

    const { items, canteenId } = get();

    if (canteenId !== null && canteenId !== product.canteen_id) {
      throw new CartCanteenConflictError();
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
      total: calculateCartTotal(nextItems),
    });
  },

  replaceCart(product: Product, quantity = 1): void {
    if (quantity <= 0) {
      throw new Error('Quantity must be greater than zero.');
    }
    const nextItems = [{ product, quantity }];
    set({
      items: nextItems,
      canteenId: product.canteen_id,
      total: calculateCartTotal(nextItems),
    });
  },

  removeItem(productId: string): void {
    const { items } = get();
    const nextItems = items.filter((item) => item.product.id !== productId);

    set({
      items: nextItems,
      canteenId: nextItems.length > 0 ? nextItems[0].product.canteen_id : null,
      total: calculateCartTotal(nextItems),
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
      total: calculateCartTotal(nextItems),
    });
  },

  clearCart(): void {
    set({
      items: [],
      canteenId: null,
      total: 0,
    });
  },
}), {
  name: 'ilarica-cart',
  version: 1,
  partialize: (state) => ({
    items: state.items,
    canteenId: state.canteenId,
    total: state.total,
  }),
  merge: (persistedState, currentState) => {
    const persisted = persistedState as Partial<CartState>;
    const items = sanitizePersistedItems(persisted.items);
    return {
      ...currentState,
      items,
      canteenId: items[0]?.product.canteen_id ?? null,
      total: calculateCartTotal(items),
    };
  },
}));
