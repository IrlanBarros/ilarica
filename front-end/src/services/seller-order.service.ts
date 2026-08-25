import { apiClient } from '../api';
import type { SellerOrder, SellerOrderStatusUpdate } from '../types';

export async function listSellerOrders(): Promise<SellerOrder[]> {
  const response = await apiClient.get<SellerOrder[]>('/canteens/me/orders');
  return response.data;
}

export async function updateSellerOrderStatus(orderId: string, payload: SellerOrderStatusUpdate): Promise<SellerOrder> {
  const response = await apiClient.patch<SellerOrder>(`/canteens/me/orders/${orderId}/status`, payload);
  return response.data;
}
