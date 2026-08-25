import { apiClient } from '../api';
import type {
  ApiMessageResponse,
  TransportKit,
  TransportKitCreate,
  TransportKitUpdate,
} from '../types';

export async function listTransportKits(): Promise<TransportKit[]> {
  const response = await apiClient.get<TransportKit[]>('/transport-kits/');
  return response.data;
}

export async function getTransportKit(kitId: string): Promise<TransportKit> {
  const response = await apiClient.get<TransportKit>(`/transport-kits/${kitId}`);
  return response.data;
}

export async function createTransportKit(payload: TransportKitCreate): Promise<TransportKit> {
  const response = await apiClient.post<TransportKit>('/transport-kits/', payload);
  return response.data;
}

export async function updateTransportKit(kitId: string, payload: TransportKitUpdate): Promise<TransportKit> {
  const response = await apiClient.patch<TransportKit>(`/transport-kits/${kitId}`, payload);
  return response.data;
}

export async function deleteTransportKit(kitId: string): Promise<ApiMessageResponse> {
  const response = await apiClient.delete<ApiMessageResponse>(`/transport-kits/${kitId}`);
  return response.data;
}