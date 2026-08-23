export type DeliveryRideStatus =
  | 'draft'
  | 'queued'
  | 'accepted'
  | 'arrived'
  | 'completed';

export interface DeliveryRideBase {
  drop_off_zone_id: string;
  status: DeliveryRideStatus;
  assigned_courier_id: string | null;
  is_arrived: boolean;
}

export interface DeliveryRide extends DeliveryRideBase {
  id: string;
}

export interface DeliveryRideCreate {
  drop_off_zone_id: string;
  status?: DeliveryRideStatus;
  assigned_courier_id?: string | null;
  is_arrived?: boolean;
}

export interface DeliveryRideUpdate {
  drop_off_zone_id?: string | null;
  status?: DeliveryRideStatus | null;
  assigned_courier_id?: string | null;
  is_arrived?: boolean | null;
}