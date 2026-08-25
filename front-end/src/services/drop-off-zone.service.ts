import { apiClient } from '../api';
import type {
  ApiMessageResponse,
  DropOffZone,
  DropOffZoneCreate,
  DropOffZoneUpdate,
} from '../types';

export async function listDropOffZones(): Promise<DropOffZone[]> {
  const response = await apiClient.get<DropOffZone[]>('/drop-off-zones/');
  return response.data;
}

export async function getDropOffZone(zoneId: string): Promise<DropOffZone> {
  const response = await apiClient.get<DropOffZone>(`/drop-off-zones/${zoneId}`);
  return response.data;
}

export async function createDropOffZone(payload: DropOffZoneCreate): Promise<DropOffZone> {
  const response = await apiClient.post<DropOffZone>('/drop-off-zones/', payload);
  return response.data;
}

export async function updateDropOffZone(zoneId: string, payload: DropOffZoneUpdate): Promise<DropOffZone> {
  const response = await apiClient.patch<DropOffZone>(`/drop-off-zones/${zoneId}`, payload);
  return response.data;
}

export async function deleteDropOffZone(zoneId: string): Promise<ApiMessageResponse> {
  const response = await apiClient.delete<ApiMessageResponse>(`/drop-off-zones/${zoneId}`);
  return response.data;
}