import { apiClient } from '../api';
import type { ApiMessageResponse, Product, ProductCreate, ProductUpdate } from '../types';

export async function listProducts(): Promise<Product[]> {
  const response = await apiClient.get<Product[]>('/products/');

  return response.data;
}

export async function getProduct(productId: string): Promise<Product> {
  const response = await apiClient.get<Product>(`/products/${productId}`);

  return response.data;
}

export async function createProduct(payload: ProductCreate): Promise<Product> {
  const response = await apiClient.post<Product>('/products/', payload);

  return response.data;
}

export async function updateProduct(productId: string, payload: ProductUpdate): Promise<Product> {
  const response = await apiClient.patch<Product>(`/products/${productId}`, payload);

  return response.data;
}

export async function deleteProduct(productId: string): Promise<ApiMessageResponse> {
  const response = await apiClient.delete<ApiMessageResponse>(`/products/${productId}`);

  return response.data;
}

export async function listMyCanteenProducts(): Promise<Product[]> {
  return (await apiClient.get<Product[]>('/canteens/me/products')).data;
}

export async function createMyCanteenProduct(payload: ProductCreate): Promise<Product> {
  return (await apiClient.post<Product>('/canteens/me/products', payload)).data;
}

export async function updateMyCanteenProduct(productId: string, payload: ProductUpdate): Promise<Product> {
  return (await apiClient.patch<Product>(`/canteens/me/products/${productId}`, payload)).data;
}

export async function deleteMyCanteenProduct(productId: string): Promise<void> {
  await apiClient.delete(`/canteens/me/products/${productId}`);
}
