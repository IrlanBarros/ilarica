export interface TransportKitBase {
  serial_number: string;
  is_allocated: boolean;
  courier_id: string | null;
}

export interface TransportKit extends TransportKitBase {
  id: string;
}

export interface TransportKitCreate {
  serial_number: string;
  is_allocated?: boolean;
  courier_id?: string | null;
}

export interface TransportKitUpdate {
  serial_number?: string | null;
  is_allocated?: boolean | null;
  courier_id?: string | null;
}