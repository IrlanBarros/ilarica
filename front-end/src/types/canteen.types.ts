export interface CanteenBusinessHoursEntry {
  day: 'weekdays' | 'saturday' | 'sunday';
  opens_at: string;
  closes_at: string;
  is_open: boolean;
}

export interface CanteenBase {
  name: string;
  location: string;
  is_open: boolean;
  products: string[];
  opening_hours?: CanteenBusinessHoursEntry[];
}

export interface Canteen extends CanteenBase {
  id: string;
  user_id: string;
}

export interface CanteenCreate {
  name: string;
  location: string;
  user_id: string;
  is_open?: boolean;
}

export interface CanteenUpdate {
  name?: string | null;
  location?: string | null;
  is_open?: boolean | null;
  opening_hours?: CanteenBusinessHoursEntry[] | null;
}
