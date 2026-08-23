import type { Money } from './api.types';

export type KnownOrderStatus =
  | 'draft'
  | 'Awaiting Payment'
  | 'paid'
  | 'in_transit'
  | 'ready_for_pickup'
  | 'completed';

export type OrderStatus = KnownOrderStatus | (string & {});

export interface OrderItemBase {
  product_id: string;
  quantity: number;
  unit_price: Money;
}

export interface OrderItem extends OrderItemBase {
  id: string;
}

export interface OrderItemCreate extends OrderItemBase {}

export interface OrderItemUpdate {
  product_id?: string | null;
  quantity?: number | null;
  unit_price?: Money | null;
}

export interface OrderBase {
  customer_id: string;
  canteen_id: string;
  drop_off_zone_id: string;
  status: OrderStatus;
  total_amount: Money;
}

export interface Order extends OrderBase {
  id: string;
  items: OrderItem[];
  pickup_pin: string | null;
}

export interface OrderCreate {
  customer_id: string;
  canteen_id: string;
  drop_off_zone_id: string;
  items: [OrderItemCreate, ...OrderItemCreate[]];
  status?: OrderStatus;
  total_amount?: Money;
}

export interface OrderUpdate {
  status?: OrderStatus | null;
  total_amount?: Money | null;
  pickup_pin?: string | null;
}