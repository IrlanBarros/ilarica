import { apiClient } from '../api';
import type { Wallet } from '../types';

export async function getMyWallet(): Promise<Wallet> {
  const response = await apiClient.get<Wallet>('/wallets/me');
  return response.data;
}
