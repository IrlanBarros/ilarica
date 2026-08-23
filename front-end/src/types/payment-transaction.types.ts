import type { Money } from './api.types';

export type PaymentTransactionStatus = 'pending' | 'processing' | 'succeeded' | 'failed';

export interface PaymentTransactionBase {
  order_id: string;
  amount: Money;
  payment_method: string;
  status: PaymentTransactionStatus;
  external_reference: string | null;
}

export interface PaymentTransaction extends PaymentTransactionBase {
  id: string;
}

export interface PaymentTransactionCreate {
  order_id: string;
  amount: Money;
  payment_method: string;
  status?: PaymentTransactionStatus;
  external_reference?: string | null;
}

export interface PaymentTransactionUpdate {
  order_id?: string | null;
  amount?: Money | null;
  payment_method?: string | null;
  status?: PaymentTransactionStatus | null;
  external_reference?: string | null;
}