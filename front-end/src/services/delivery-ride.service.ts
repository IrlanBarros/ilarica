import { apiClient } from '../api';
import type {
  ApiMessageResponse,
  DeliveryRide,
  DeliveryRideCreate,
  DeliveryRideUpdate,
} from '../types';

export async function listDeliveryRides(): Promise<DeliveryRide[]> {
  const response = await apiClient.get<DeliveryRide[]>('/delivery-rides/');
  return response.data;
}

export async function getDeliveryRide(rideId: string): Promise<DeliveryRide> {
  const response = await apiClient.get<DeliveryRide>(`/delivery-rides/${rideId}`);
  return response.data;
}

export async function createDeliveryRide(payload: DeliveryRideCreate): Promise<DeliveryRide> {
  const response = await apiClient.post<DeliveryRide>('/delivery-rides/', payload);
  return response.data;
}

export async function updateDeliveryRide(rideId: string, payload: DeliveryRideUpdate): Promise<DeliveryRide> {
  const response = await apiClient.patch<DeliveryRide>(`/delivery-rides/${rideId}`, payload);
  return response.data;
}

export async function deleteDeliveryRide(rideId: string): Promise<ApiMessageResponse> {
  const response = await apiClient.delete<ApiMessageResponse>(`/delivery-rides/${rideId}`);
  return response.data;
}