import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import type { PaymentMethod } from '../types';

interface PendingPayment {
  orderId: string;
  transactionId: string | null;
  idempotencyKey: string;
  method: PaymentMethod;
}

interface PaymentState {
  pending: PendingPayment | null;
  start: (payment: PendingPayment) => void;
  setTransaction: (transactionId: string) => void;
  clear: () => void;
}

export const usePaymentStore = create<PaymentState>()(persist((set) => ({
  pending: null,
  start(payment): void {
    set({ pending: payment });
  },
  setTransaction(transactionId): void {
    set((state) => ({
      pending: state.pending ? { ...state.pending, transactionId } : null,
    }));
  },
  clear(): void {
    set({ pending: null });
  },
}), { name: 'ilarica-payment', version: 1 }));
