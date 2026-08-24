import { render, screen } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { apiClient } from '../api';
import { useAuthStore, useCartStore } from '../store';
import { PaymentConfirmedPage } from './PaymentConfirmedPage';

describe('PaymentConfirmedPage', () => {
  let mock: MockAdapter;
  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    useCartStore.getState().clearCart();
    useAuthStore.setState({ user: { id: 'customer-1', name: 'Matheus Silva', email: 'matheus@aluno.ufca.edu.br', whatsapp: '5588999999999', role: 'customer', is_active: true, is_email_validated: true } });
  });

  it('shows confirmation only after validating the transaction with the backend', async () => {
    mock.onGet('/payment-transactions/payment-1').reply(200, { id: 'payment-1', order_id: 'order-1', amount: '18.00', payment_method: 'pix', status: 'succeeded', external_reference: 'pix-1', pix_copy_paste: null, pix_qr_code: null, expires_at: null, failure_reason: null, created_at: '2026-08-24T10:00:00Z', confirmed_at: '2026-08-24T10:01:00Z' });
    render(<MemoryRouter initialEntries={['/pedidos/order-1/pagamento-confirmado?transaction=payment-1']}><Routes><Route path="/pedidos/:orderId/pagamento-confirmado" element={<PaymentConfirmedPage />} /></Routes></MemoryRouter>);
    expect(await screen.findByRole('heading', { name: 'Pagamento Confirmado!' })).toBeTruthy();
    expect(screen.getByText('R$ 18,00')).toBeTruthy();
    expect(screen.getByText('Pix')).toBeTruthy();
  });

  it('refuses to display success without server evidence', async () => {
    render(<MemoryRouter initialEntries={['/pedidos/order-1/pagamento-confirmado']}><Routes><Route path="/pedidos/:orderId/pagamento-confirmado" element={<PaymentConfirmedPage />} /></Routes></MemoryRouter>);
    expect(await screen.findByRole('heading', { name: 'Pagamento não validado' })).toBeTruthy();
  });
});
