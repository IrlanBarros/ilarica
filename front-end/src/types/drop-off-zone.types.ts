export interface DropOffZoneBase {
  name: string;
  capacity_total: number;
  current_load: number;
  is_active: boolean;
}

export interface DropOffZone extends DropOffZoneBase {
  id: string;
}

export interface DropOffZoneCreate {
  name: string;
  capacity_total: number;
  current_load?: number;
  is_active?: boolean;
}

export interface DropOffZoneUpdate {
  name?: string | null;
  capacity_total?: number | null;
  current_load?: number | null;
  is_active?: boolean | null;
}