export type SellerSection = 'menu' | 'orders' | 'hours' | 'settings';

export interface SellerMenuItem {
  id: string;
  name: string;
  description: string;
  price: string;
  imageUrl: string;
  isAvailable: boolean;
}

export interface BusinessHoursEntry {
  id: 'weekdays' | 'saturday' | 'sunday';
  label: string;
  opensAt: string;
  closesAt: string;
  isOpen: boolean;
}

export type SellerOrderStage = 'new' | 'preparing' | 'ready';

export interface SellerOrderLine {
  productId: string;
  name: string;
  quantity: number;
}

/**
 * View model expected from a future canteen-scoped orders endpoint.
 * IDs remain UUID strings and financial values remain server-provided strings.
 */
export interface SellerOrder {
  id: string;
  displayCode: string;
  customerName: string;
  createdAt: string;
  fulfillment: 'pickup' | 'delivery';
  destination: string;
  items: SellerOrderLine[];
  totalAmount: string;
  stage: SellerOrderStage;
  notes?: string;
}
