import { apiClient } from '../api';
import type {
  ApiMessageResponse,
  PaymentTransaction,
  PaymentTransactionCreate,
  PaymentTransactionUpdate,
} from '../types';

export async function listPaymentTransactions(): Promise<PaymentTransaction[]> {
  const response = await apiClient.get<PaymentTransaction[]>('/payment-transactions/');
  return response.data;
}

export async function getPaymentTransaction(transactionId: string): Promise<PaymentTransaction> {
  const response = await apiClient.get<PaymentTransaction>(`/payment-transactions/${transactionId}`);
  return response.data;
}

export async function createPaymentTransaction(payload: PaymentTransactionCreate): Promise<PaymentTransaction> {
  const response = await apiClient.post<PaymentTransaction>('/payment-transactions/', payload);
  return response.data;
}

export async function updatePaymentTransaction(
  transactionId: string,
  payload: PaymentTransactionUpdate,
): Promise<PaymentTransaction> {
  const response = await apiClient.patch<PaymentTransaction>(`/payment-transactions/${transactionId}`, payload);
  return response.data;
}

export async function deletePaymentTransaction(transactionId: string): Promise<ApiMessageResponse> {
  const response = await apiClient.delete<ApiMessageResponse>(`/payment-transactions/${transactionId}`);
  return response.data;
}