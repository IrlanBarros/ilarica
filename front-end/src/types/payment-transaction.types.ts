import type { Money } from './api.types';

export type PaymentMethod = 'pix' | 'wallet';
export type PaymentTransactionStatus = 'pending' | 'processing' | 'succeeded' | 'failed' | 'expired';

export interface PaymentTransaction {
  id: string;
  order_id: string;
  amount: Money;
  payment_method: PaymentMethod;
  status: PaymentTransactionStatus;
  external_reference: string | null;
  pix_copy_paste: string | null;
  pix_qr_code: string | null;
  expires_at: string | null;
  failure_reason: string | null;
  created_at: string;
  confirmed_at: string | null;
}

export interface PaymentIntentCreate {
  order_id: string;
  payment_method: PaymentMethod;
}

export type PaymentTransactionCreate = PaymentIntentCreate;
