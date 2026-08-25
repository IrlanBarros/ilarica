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
