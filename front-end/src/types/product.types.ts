import type { Money } from './api.types';

export interface ProductBase {
  name: string;
  description: string | null;
  price: Money;
  is_active: boolean;
}

export interface Product extends ProductBase {
  id: string;
  canteen_id: string;
  is_fast_stock_enabled: boolean;
}

export interface ProductCreate {
  name: string;
  canteen_id: string;
  price: Money;
  description?: string | null;
  is_active?: boolean;
}

export interface ProductUpdate {
  name?: string | null;
  description?: string | null;
  price?: Money | null;
  is_active?: boolean | null;
}