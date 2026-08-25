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

function isPendingPayment(value: unknown): value is PendingPayment {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<PendingPayment>;
  return typeof candidate.orderId === 'string'
    && (candidate.transactionId === null || typeof candidate.transactionId === 'string')
    && typeof candidate.idempotencyKey === 'string'
    && (candidate.method === 'pix' || candidate.method === 'wallet');
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
}), {
  name: 'ilarica-payment',
  version: 1,
  partialize: (state) => ({ pending: state.pending }),
  merge: (persistedState, currentState) => {
    const candidate = (persistedState as Partial<PaymentState>).pending;
    return { ...currentState, pending: isPendingPayment(candidate) ? candidate : null };
  },
}));
