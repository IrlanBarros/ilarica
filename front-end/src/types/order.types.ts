import type { Money } from './api.types';

export type KnownOrderStatus =
  | 'draft'
  | 'Awaiting Payment'
  | 'paid'
  | 'preparing'
  | 'in_transit'
  | 'ready_for_pickup'
  | 'completed';

export type OrderStatus = KnownOrderStatus | (string & {});
export type FulfillmentType = 'pickup' | 'delivery';

export interface OrderItemBase {
  product_id: string;
  quantity: number;
  unit_price: Money;
}

export interface OrderItem extends OrderItemBase {
  id: string;
}

export interface OrderItemCreate {
  product_id: string;
  quantity: number;
}

export interface OrderItemUpdate {
  product_id?: string | null;
  quantity?: number | null;
  unit_price?: Money | null;
}

export interface OrderBase {
  customer_id: string;
  canteen_id: string;
  fulfillment_type?: FulfillmentType;
  drop_off_zone_id: string | null;
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
  fulfillment_type?: FulfillmentType;
  drop_off_zone_id: string | null;
  items: [OrderItemCreate, ...OrderItemCreate[]];
}

export interface OrderUpdate {
  status?: OrderStatus | null;
  total_amount?: Money | null;
  pickup_pin?: string | null;
}

export interface CustomerOrder {
  id: string;
  canteen_id: string;
  status: OrderStatus;
  fulfillment_type: FulfillmentType;
  items: Array<{ id: string; product_id: string; name: string; quantity: number; unit_price: Money }>;
  total_amount: Money;
  destination: { id: string; name: string; description: string | null } | null;
  canteen: { id: string; name: string; location: string };
  pickup_pin: string | null;
}
