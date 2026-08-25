import { apiClient } from '../api';
import type { ApiMessageResponse, Canteen, CanteenCreate, CanteenUpdate } from '../types';

export async function listCanteens(): Promise<Canteen[]> {
  const response = await apiClient.get<Canteen[]>('/canteens/');
  return response.data;
}

export async function getCanteen(canteenId: string): Promise<Canteen> {
  const response = await apiClient.get<Canteen>(`/canteens/${canteenId}`);
  return response.data;
}

export async function createCanteen(payload: CanteenCreate): Promise<Canteen> {
  const response = await apiClient.post<Canteen>('/canteens/', payload);
  return response.data;
}

export async function updateCanteen(canteenId: string, payload: CanteenUpdate): Promise<Canteen> {
  const response = await apiClient.patch<Canteen>(`/canteens/${canteenId}`, payload);
  return response.data;
}

export async function deleteCanteen(canteenId: string): Promise<ApiMessageResponse> {
  const response = await apiClient.delete<ApiMessageResponse>(`/canteens/${canteenId}`);
  return response.data;
}

export async function getMyCanteen(): Promise<Canteen> {
  return (await apiClient.get<Canteen>('/canteens/me')).data;
}

export async function updateMyCanteen(payload: CanteenUpdate): Promise<Canteen> {
  return (await apiClient.patch<Canteen>('/canteens/me', payload)).data;
}
