import { apiClient } from '../api';
import type { ApiMessageResponse, CustomerOrder, Order, OrderCreate, OrderUpdate } from '../types';

export async function listOrders(): Promise<Order[]> {
  const response = await apiClient.get<Order[]>('/orders/');

  return response.data;
}

export async function getOrder(orderId: string): Promise<Order> {
  const response = await apiClient.get<Order>(`/orders/${orderId}`);

  return response.data;
}

export async function createOrder(payload: OrderCreate): Promise<Order> {
  const response = await apiClient.post<Order>('/orders/', payload);

  return response.data;
}

export async function updateOrder(orderId: string, payload: OrderUpdate): Promise<Order> {
  const response = await apiClient.patch<Order>(`/orders/${orderId}`, payload);

  return response.data;
}

export async function deleteOrder(orderId: string): Promise<ApiMessageResponse> {
  const response = await apiClient.delete<ApiMessageResponse>(`/orders/${orderId}`);

  return response.data;
}

export async function listMyOrders(): Promise<CustomerOrder[]> {
  return (await apiClient.get<CustomerOrder[]>('/orders/me')).data;
}
