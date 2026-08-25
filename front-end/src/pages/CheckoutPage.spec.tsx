import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { apiClient } from '../api';
import { useAuthStore, useCartStore, usePaymentStore } from '../store';
import type { Order, PaymentTransaction, Product } from '../types';
import { CheckoutPage } from './CheckoutPage';

const product: Product = { id: 'product-1', canteen_id: 'canteen-1', name: 'Coxinha Suprema', description: null, price: '6.50', is_active: true, is_fast_stock_enabled: false };
const order: Order = { id: 'order-1', customer_id: 'customer-1', canteen_id: 'canteen-1', drop_off_zone_id: 'zone-1', status: 'draft', total_amount: '13.00', items: [{ id: 'item-1', product_id: 'product-1', quantity: 2, unit_price: '6.50' }], pickup_pin: null };

function transaction(overrides: Partial<PaymentTransaction> = {}): PaymentTransaction {
  return { id: 'payment-1', order_id: 'order-1', amount: '13.00', payment_method: 'pix', status: 'pending', external_reference: 'pix-1', pix_copy_paste: 'pix-code', pix_qr_code: 'data:image/svg+xml;base64,abc', expires_at: '2099-01-01T00:00:00Z', failure_reason: null, created_at: '2026-08-24T10:00:00Z', confirmed_at: null, ...overrides };
}

function renderCheckout(): void {
  render(<MemoryRouter initialEntries={['/checkout']}><Routes>
    <Route path="/checkout" element={<CheckoutPage />} />
    <Route path="/pagamentos/:transactionId/pix" element={<p>Pagamento Pix</p>} />
    <Route path="/pedidos/:orderId/pagamento-confirmado" element={<p>Pagamento confirmado</p>} />
  </Routes></MemoryRouter>);
}

describe('CheckoutPage', () => {
  let mock: MockAdapter;
  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    useCartStore.getState().clearCart();
    useCartStore.getState().addItem(product, 2);
    usePaymentStore.getState().clear();
    useAuthStore.setState({ user: { id: 'customer-1', name: 'Matheus Silva', email: 'matheus@aluno.ufca.edu.br', whatsapp: '5588999999999', role: 'customer', is_active: true, is_email_validated: true } });
    mock.onGet('/drop-off-zones/').reply(200, [{ id: 'zone-1', name: 'Bloco C', capacity_total: 10, current_load: 2, is_active: true }]);
  });

  it('creates a server-priced order and Pix intent without clearing the cart', async () => {
    mock.onPost('/orders/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual({ customer_id: 'customer-1', canteen_id: 'canteen-1', fulfillment_type: 'delivery', drop_off_zone_id: 'zone-1', items: [{ product_id: 'product-1', quantity: 2 }] });
      return [201, order];
    });
    mock.onPost('/payment-transactions/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual({ order_id: 'order-1', payment_method: 'pix' });
      expect(config.headers?.['Idempotency-Key']).toBeTruthy();
      return [201, transaction()];
    });
    renderCheckout();
    await screen.findByRole('option', { name: 'Bloco C' });
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar e Pagar' }));
    await screen.findByText('Pagamento Pix');
    expect(useCartStore.getState().items).toHaveLength(1);
    expect(usePaymentStore.getState().pending?.transactionId).toBe('payment-1');
  });

  it('clears the cart only after an atomic wallet payment succeeds', async () => {
    mock.onGet('/wallets/me').reply(200, { id: 'wallet-1', customer_id: 'customer-1', balance: '40.00' });
    mock.onPost('/orders/').reply(201, order);
    mock.onPost('/payment-transactions/').reply(201, transaction({ payment_method: 'wallet', status: 'succeeded', pix_copy_paste: null, pix_qr_code: null, expires_at: null, confirmed_at: '2026-08-24T10:01:00Z' }));
    renderCheckout();
    await screen.findByRole('option', { name: 'Bloco C' });
    fireEvent.click(screen.getByRole('button', { name: 'Carteira Digital' }));
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar e Pagar' }));
    await screen.findByText('Pagamento confirmado');
    expect(useCartStore.getState().items).toHaveLength(0);
  });

  it('preserves the cart and explains insufficient wallet balance', async () => {
    mock.onGet('/wallets/me').reply(200, { id: 'wallet-1', customer_id: 'customer-1', balance: '1.00' });
    mock.onPost('/orders/').reply(201, order);
    mock.onPost('/payment-transactions/').reply(402, { detail: 'Saldo insuficiente.' });
    renderCheckout();
    await screen.findByRole('option', { name: 'Bloco C' });
    fireEvent.click(screen.getByRole('button', { name: 'Carteira Digital' }));
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar e Pagar' }));
    expect((await screen.findByRole('alert')).textContent).toContain('Saldo insuficiente');
    expect(useCartStore.getState().items).toHaveLength(1);
  });

  it('keeps the cart when the API rejects an unavailable product', async () => {
    mock.onPost('/orders/').reply(409, { detail: 'Product is unavailable' });
    renderCheckout();
    await screen.findByRole('option', { name: 'Bloco C' });
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar e Pagar' }));
    expect((await screen.findByRole('alert')).textContent).toContain('não está mais disponível');
    expect(useCartStore.getState().items).toHaveLength(1);
  });

  it('prevents submission while there is no available zone', async () => {
    mock.resetHandlers();
    mock.onGet('/drop-off-zones/').reply(200, [{ id: 'zone-full', name: 'Bloco Lotado', capacity_total: 10, current_load: 10, is_active: true }]);
    renderCheckout();
    await waitFor(() => expect(screen.getByText('Nenhum ponto está disponível no momento.')).toBeTruthy());
    expect((screen.getByRole('button', { name: 'Confirmar e Pagar' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('allows pickup checkout without a delivery zone', async () => {
    mock.resetHandlers();
    mock.onGet('/drop-off-zones/').reply(200, []);
    renderCheckout();
    await waitFor(() => expect(screen.getByText('Nenhum ponto está disponível no momento.')).toBeTruthy());
    fireEvent.click(screen.getByRole('button', { name: /Retirada presencial/ }));
    expect((screen.getByRole('button', { name: 'Confirmar e Pagar' }) as HTMLButtonElement).disabled).toBe(false);
  });
});
