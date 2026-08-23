import type { Money } from './api.types';

export interface WalletBase {
  user_id: string;
  balance: Money;
  pending_withdrawal: Money;
}

export interface Wallet extends WalletBase {
  id: string;
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