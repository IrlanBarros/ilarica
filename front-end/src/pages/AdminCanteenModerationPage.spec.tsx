import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { apiClient } from '../api';
import { AdminCanteenModerationPage } from './AdminCanteenModerationPage';

const pendingCanteen = {
  id: 'canteen-1', user_id: 'staff-1', name: 'Cantina Central', location: 'Bloco H',
  description: 'Lanches artesanais preparados diariamente no campus.',
  logo_url: 'https://images.example/logo.png', is_open: false, products: [], opening_hours: [],
  commercial_terms_accepted_at: '2026-08-25T12:00:00Z', moderation_status: 'pending',
};

describe('AdminCanteenModerationPage', () => {
  it('lists pending registrations and approves one through the admin endpoint', async () => {
    const mock = new MockAdapter(apiClient);
    mock.onGet('/canteens/moderation').reply(200, [pendingCanteen]);
    mock.onPatch('/canteens/canteen-1/moderation').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual({ status: 'approved', rejection_reason: null });
      return [200, { ...pendingCanteen, moderation_status: 'approved' }];
    });
    render(<MemoryRouter><AdminCanteenModerationPage /></MemoryRouter>);

    expect(await screen.findByText('Cantina Central')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Aprovar' }));
    await waitFor(() => expect(screen.getByText('Nenhuma solicitação pendente')).toBeTruthy());
  });

  it('requires a clear reason before rejecting a registration', async () => {
    const mock = new MockAdapter(apiClient);
    mock.onGet('/canteens/moderation').reply(200, [pendingCanteen]);
    mock.onPatch('/canteens/canteen-1/moderation').reply(200, { ...pendingCanteen, moderation_status: 'rejected' });
    render(<MemoryRouter><AdminCanteenModerationPage /></MemoryRouter>);

    await screen.findByText('Cantina Central');
    fireEvent.click(screen.getByRole('button', { name: 'Rejeitar' }));
    const confirm = screen.getByRole('button', { name: 'Confirmar rejeição' });
    expect(confirm).toHaveProperty('disabled', true);
    fireEvent.change(screen.getByLabelText('Motivo da rejeição'), { target: { value: 'Atualize a logo enviada.' } });
    fireEvent.click(confirm);
    await waitFor(() => expect(screen.getByText('Nenhuma solicitação pendente')).toBeTruthy());
  });
});
