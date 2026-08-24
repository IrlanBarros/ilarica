export interface CanteenBase {
  name: string;
  location: string;
  is_open: boolean;
  products: string[];
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
}
