import { apiClient } from '../api';
import type { PaymentIntentCreate, PaymentTransaction } from '../types';

export async function listPaymentTransactions(): Promise<PaymentTransaction[]> {
  const response = await apiClient.get<PaymentTransaction[]>('/payment-transactions/');
  return response.data;
}

export async function getPaymentTransaction(transactionId: string): Promise<PaymentTransaction> {
  const response = await apiClient.get<PaymentTransaction>(`/payment-transactions/${transactionId}`);
  return response.data;
}

export async function createPaymentTransaction(
  payload: PaymentIntentCreate,
  idempotencyKey: string,
): Promise<PaymentTransaction> {
  const response = await apiClient.post<PaymentTransaction>('/payment-transactions/', payload, {
    headers: { 'Idempotency-Key': idempotencyKey },
  });
  return response.data;
}
