import type { Money } from './api.types';

export interface WalletBase {
  user_id: string;
  balance: Money;
  pending_withdrawal: Money;
}

export interface Wallet extends WalletBase {
  id: string;
}

export interface WalletStatementEntry {
  id: string;
  orderId: string;
  kind: 'payment' | 'top_up';
  amount: Money;
  status: 'pending' | 'processing' | 'succeeded' | 'failed' | 'expired';
  occurredAt: string;
}

export interface WalletCreate {
  user_id: string;
  balance?: Money;
  pending_withdrawal?: Money;
}

export interface WalletUpdate {
  balance?: Money | null;
  pending_withdrawal?: Money | null;
}
