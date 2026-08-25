import { render, screen } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { apiClient } from '../api';
import { WalletPage } from './WalletPage';

describe('WalletPage', () => {
  it('renders the authenticated balance and transaction statement', async () => {
    const mock = new MockAdapter(apiClient);
    mock.onGet('/wallets/me').reply(200, { id: 'wallet-id', user_id: 'user-id', balance: '31.50', pending_withdrawal: '0.00' });
    mock.onGet('/payment-transactions/').reply(200, [{ id: 'tx-id', order_id: '40810000-0000-4000-8000-000000000001', amount: '18.00', payment_method: 'wallet', status: 'succeeded', external_reference: null, pix_copy_paste: null, pix_qr_code: null, expires_at: null, failure_reason: null, created_at: '2026-08-25T12:00:00Z', confirmed_at: '2026-08-25T12:00:01Z' }]);
    render(<MemoryRouter><WalletPage /></MemoryRouter>);
    expect(await screen.findByText(/31,50/)).toBeTruthy();
    expect(screen.getByText(/Pagamento do pedido #40810000/)).toBeTruthy();
  });
});
