import { apiClient } from '../api';
import type { SellerOrder, SellerOrderStatusUpdate, SellerPickupConfirmationResponse } from '../types';

export async function listSellerOrders(): Promise<SellerOrder[]> {
  const response = await apiClient.get<SellerOrder[]>('/canteens/me/orders');
  return response.data;
}

export async function listSellerOrderHistory(): Promise<SellerOrder[]> {
  const response = await apiClient.get<SellerOrder[]>('/canteens/me/orders/history');
  return response.data;
}

export async function confirmSellerOrderPickup(orderId: string, pickupPin: string): Promise<SellerPickupConfirmationResponse> {
  const response = await apiClient.post<SellerPickupConfirmationResponse>(`/canteens/me/orders/${orderId}/pickup/confirm`, { pickup_pin: pickupPin });
  return response.data;
}

export async function updateSellerOrderStatus(orderId: string, payload: SellerOrderStatusUpdate): Promise<SellerOrder> {
  const response = await apiClient.patch<SellerOrder>(`/canteens/me/orders/${orderId}/status`, payload);
  return response.data;
}
