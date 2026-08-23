import { apiClient } from '../api';
import type { ApiMessageResponse, Wallet, WalletCreate, WalletUpdate } from '../types';

export async function listWallets(): Promise<Wallet[]> {
  const response = await apiClient.get<Wallet[]>('/wallets/');

  return response.data;
}

export async function getWallet(walletId: string): Promise<Wallet> {
  const response = await apiClient.get<Wallet>(`/wallets/${walletId}`);

  return response.data;
}

export async function createWallet(payload: WalletCreate): Promise<Wallet> {
  const response = await apiClient.post<Wallet>('/wallets/', payload);

  return response.data;
}

export async function updateWallet(walletId: string, payload: WalletUpdate): Promise<Wallet> {
  const response = await apiClient.patch<Wallet>(`/wallets/${walletId}`, payload);

  return response.data;
}

export async function deleteWallet(walletId: string): Promise<ApiMessageResponse> {
  const response = await apiClient.delete<ApiMessageResponse>(`/wallets/${walletId}`);

  return response.data;
}