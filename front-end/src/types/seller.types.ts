export type SellerSection = 'menu' | 'orders' | 'hours' | 'settings';

export interface SellerMenuItem {
  id: string;
  name: string;
  description: string;
  price: string;
  imageUrl: string;
  isAvailable: boolean;
  category: import('./product.types').ProductCategory;
  stockQuantity: number;
}

export interface BusinessHoursEntry {
  id: 'weekdays' | 'saturday' | 'sunday';
  label: string;
  opensAt: string;
  closesAt: string;
  isOpen: boolean;
}

export type SellerOrderStatus = 'paid' | 'preparing' | 'ready_for_pickup' | 'completed';
export type SellerOrderStage = 'new' | 'preparing' | 'ready' | 'history';

export interface SellerOrderCustomer {
  id: string;
  name: string;
}

export interface SellerOrderDestination {
  id: string;
  name: string;
  description: string | null;
}

export interface SellerOrderLine {
  id: string;
  product_id: string;
  name: string;
  quantity: number;
  unit_price: string;
}

export interface SellerOrder {
  id: string;
  canteen_id: string;
  status: SellerOrderStatus;
  items: SellerOrderLine[];
  total_amount: string;
  customer: SellerOrderCustomer;
  fulfillment_type: 'pickup' | 'delivery';
  destination: SellerOrderDestination | null;
  location_details: string | null;
}

export interface SellerPickupConfirmationResponse {
  id: string;
  status: 'completed';
}

export interface SellerOrderStatusUpdate {
  status: Exclude<SellerOrderStatus, 'paid'>;
}
