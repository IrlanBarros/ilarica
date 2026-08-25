import { render, screen } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { apiClient } from '../api';
import { useCartStore, usePaymentStore } from '../store';
import type { Product } from '../types';
import { PixPaymentPage } from './PixPaymentPage';

const product: Product = { id: 'product-1', canteen_id: 'canteen-1', name: 'Coxinha', description: null, price: '6.50', is_active: true, is_fast_stock_enabled: false, category: 'salgados', stock_quantity: 20 };

function renderPage(): void {
  render(<MemoryRouter initialEntries={['/pagamentos/payment-1/pix']}><Routes>
    <Route path="/pagamentos/:transactionId/pix" element={<PixPaymentPage />} />
    <Route path="/pedidos/:orderId/pagamento-confirmado" element={<p>Confirmação validada</p>} />
  </Routes></MemoryRouter>);
}

function response(status: 'succeeded' | 'expired') {
  return { id: 'payment-1', order_id: 'order-1', amount: '13.00', payment_method: 'pix', status, external_reference: 'pix-1', pix_copy_paste: status === 'expired' ? null : 'pix-code', pix_qr_code: null, expires_at: status === 'expired' ? '2026-08-24T10:00:00Z' : '2099-01-01T00:00:00Z', failure_reason: status === 'expired' ? 'Pix payment expired' : null, created_at: '2026-08-24T09:45:00Z', confirmed_at: status === 'succeeded' ? '2026-08-24T09:46:00Z' : null };
}

describe('PixPaymentPage', () => {
  let mock: MockAdapter;
  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    useCartStore.getState().clearCart();
    useCartStore.getState().addItem(product, 2);
    usePaymentStore.getState().start({ orderId: 'order-1', transactionId: 'payment-1', idempotencyKey: 'key-00000000000001', method: 'pix' });
  });

  it('polls backend confirmation before clearing the cart and navigating', async () => {
    mock.onGet('/payment-transactions/payment-1').reply(200, response('succeeded'));
    renderPage();
    expect(await screen.findByText('Confirmação validada')).toBeTruthy();
    expect(useCartStore.getState().items).toHaveLength(0);
    expect(usePaymentStore.getState().pending).toBeNull();
  });

  it('keeps the cart when Pix expires', async () => {
    mock.onGet('/payment-transactions/payment-1').reply(200, response('expired'));
    renderPage();
    expect((await screen.findByRole('alert')).textContent).toContain('Pix expirou');
    expect(useCartStore.getState().items).toHaveLength(1);
    expect(usePaymentStore.getState().pending).toBeNull();
  });
});
