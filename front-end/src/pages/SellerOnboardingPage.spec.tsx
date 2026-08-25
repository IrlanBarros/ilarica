import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { apiClient } from '../api';
import { SellerOnboardingPage } from './SellerOnboardingPage';

const canteen = {
  id: 'canteen-1', user_id: 'staff-1', name: 'Cantina Central', location: 'Bloco H',
  description: null, logo_url: null, is_open: false, products: [], opening_hours: [],
  commercial_terms_accepted_at: null, moderation_status: 'pending',
};

describe('SellerOnboardingPage', () => {
  it('submits logo, description and explicit commercial terms acceptance', async () => {
    const mock = new MockAdapter(apiClient);
    mock.onGet('/canteens/me').reply(200, canteen);
    mock.onPost('/canteens/me/onboarding').reply((config) => {
      const payload = JSON.parse(String(config.data));
      expect(payload).toEqual({
        description: 'Lanches artesanais preparados diariamente no campus.',
        logo_url: 'https://images.example/logo.png',
        accepted_commercial_terms: true,
      });
      return [200, { ...canteen, ...payload, commercial_terms_accepted_at: '2026-08-25T12:00:00Z' }];
    });
    render(<MemoryRouter><SellerOnboardingPage /></MemoryRouter>);

    await screen.findByRole('heading', { name: 'Perfil da cantina' });
    fireEvent.change(screen.getByLabelText('URL da logo'), { target: { value: 'https://images.example/logo.png' } });
    fireEvent.change(screen.getByLabelText('Descrição do estabelecimento'), { target: { value: 'Lanches artesanais preparados diariamente no campus.' } });
    fireEvent.click(screen.getByRole('checkbox'));
    fireEvent.click(screen.getByRole('button', { name: 'Salvar e enviar para análise' }));

    await waitFor(() => expect(screen.getByRole('status').textContent).toContain('análise administrativa'));
  });

  it('shows the administrator rejection reason for resubmission', async () => {
    const mock = new MockAdapter(apiClient);
    mock.onGet('/canteens/me').reply(200, {
      ...canteen, moderation_status: 'rejected',
      rejection_reason: 'Envie uma logo com melhor resolução.',
      commercial_terms_accepted_at: '2026-08-25T12:00:00Z',
    });
    render(<MemoryRouter><SellerOnboardingPage /></MemoryRouter>);

    expect(await screen.findByText('Envie uma logo com melhor resolução.')).toBeTruthy();
    expect(screen.getByText('Ajustes solicitados')).toBeTruthy();
  });
});
