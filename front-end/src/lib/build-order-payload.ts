import type { CartItem } from '../store/useCartStore';
import type { OrderCreate, OrderItemCreate } from '../types';

interface BuildOrderPayloadInput {
  customerId: string;
  canteenId: string | null;
  dropOffZoneId: string;
  items: CartItem[];
}

export function buildOrderPayload({
  customerId,
  canteenId,
  dropOffZoneId,
  items,
}: BuildOrderPayloadInput): OrderCreate {
  if (!customerId || !canteenId || !dropOffZoneId) {
    throw new Error('Customer, canteen and drop-off zone are required to build an order.');
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
    drop_off_zone_id: dropOffZoneId,
    items: orderItems,
  };
}
