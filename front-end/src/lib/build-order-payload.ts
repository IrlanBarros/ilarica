import type { CartItem } from '../store/useCartStore';
import type { FulfillmentType, OrderCreate, OrderItemCreate } from '../types';

interface BuildOrderPayloadInput {
  customerId: string;
  canteenId: string | null;
  fulfillmentType?: FulfillmentType;
  dropOffZoneId: string | null;
  items: CartItem[];
}

export function buildOrderPayload({
  customerId,
  canteenId,
  dropOffZoneId,
  fulfillmentType,
  items,
}: BuildOrderPayloadInput): OrderCreate {
  const resolvedFulfillmentType = fulfillmentType ?? 'delivery';
  if (!customerId || !canteenId || (resolvedFulfillmentType === 'delivery' && !dropOffZoneId)) {
    throw new Error('Customer, canteen and delivery destination are required to build an order.');
  }
  if (items.length === 0) {
    throw new Error('At least one cart item is required to build an order.');
  }
  if (items.some((item) => item.product.canteen_id !== canteenId)) {
    throw new Error('All order items must belong to the selected canteen.');
  }

  const orderItems = items.map<OrderItemCreate>((item) => ({
    product_id: item.product.id,
    quantity: item.quantity,
  })) as [OrderItemCreate, ...OrderItemCreate[]];

  return {
    customer_id: customerId,
    canteen_id: canteenId,
    fulfillment_type: resolvedFulfillmentType,
    drop_off_zone_id: resolvedFulfillmentType === 'pickup' ? null : dropOffZoneId,
    items: orderItems,
  };
}
