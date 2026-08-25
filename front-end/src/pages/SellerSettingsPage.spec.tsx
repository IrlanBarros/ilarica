import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { apiClient } from '../api';
import { SellerSettingsPage } from './SellerSettingsPage';

const canteen = { id: 'canteen-id', user_id: 'user-id', name: 'Cantina Central', location: 'Bloco H', is_open: true, products: [], opening_hours: [{ day: 'weekdays', opens_at: '08:00', closes_at: '18:00', is_open: true }] };

describe('SellerSettingsPage', () => {
  it('persists real canteen settings through the owned endpoint', async () => {
    const mock = new MockAdapter(apiClient);
    mock.onGet('/canteens/me').reply(200, canteen);
    mock.onPatch('/canteens/me').reply((config) => [200, { ...canteen, ...JSON.parse(config.data as string) }]);
    render(<MemoryRouter initialEntries={['/vendedor/configuracoes']}><SellerSettingsPage mode="settings" /></MemoryRouter>);
    const name = await screen.findByDisplayValue('Cantina Central');
    fireEvent.change(name, { target: { value: 'Cantina Acadêmica' } });
    fireEvent.click(screen.getByRole('button', { name: 'Salvar configurações' }));
    await waitFor(() => expect(screen.getByRole('status').textContent).toContain('sucesso'));
  });

  it('renders persisted opening hours', async () => {
    const mock = new MockAdapter(apiClient);
    mock.onGet('/canteens/me').reply(200, canteen);
    render(<MemoryRouter initialEntries={['/vendedor/horarios']}><SellerSettingsPage mode="hours" /></MemoryRouter>);
    expect(await screen.findByDisplayValue('08:00')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Salvar horários' })).toBeTruthy();
  });
});
