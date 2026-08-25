import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { useSellerStore } from '../store';
import { apiClient } from '../api';
import { CanteenDashboardPage } from './CanteenDashboardPage';

describe('CanteenDashboardPage', () => {
  beforeEach(() => {
    const mock = new MockAdapter(apiClient);
    mock.onGet('/canteens/me/products').reply(200, [{ id: 'product-1', canteen_id: 'canteen-1', name: 'Coxinha de Frango', description: 'Crocante', price: '6.50', image_url: null, is_active: true, is_fast_stock_enabled: false }]);
    mock.onGet('/canteens/me').reply(200, { id: 'canteen-1', user_id: 'user-1', name: 'Cantina', location: 'Bloco H', is_open: true, products: ['product-1'], opening_hours: [] });
    mock.onPatch('/canteens/me/products/product-1').reply(200, { id: 'product-1', canteen_id: 'canteen-1', name: 'Coxinha de Frango', description: 'Crocante', price: '6.50', image_url: null, is_active: false, is_fast_stock_enabled: false });
    mock.onDelete('/canteens/me/products/product-1').reply(200, { detail: 'Product deleted successfully' });
    useSellerStore.setState({ activeSection: 'menu', items: [], businessHours: [] });
  });

  it('renders the seller menu from the API and handles availability', async () => {
    render(<MemoryRouter><CanteenDashboardPage /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: 'Meu Cardápio' })).toBeTruthy();
    expect(await screen.findByText('Coxinha de Frango')).toBeTruthy();
    expect(screen.getByText('Horário de Funcionamento')).toBeTruthy();

    const availability = screen.getByRole('switch', { name: 'Alterar disponibilidade de Coxinha de Frango' });
    const previous = availability.getAttribute('aria-checked');
    fireEvent.click(availability);
    await screen.findByText('Indisponível');
    expect(screen.getByRole('switch', { name: 'Alterar disponibilidade de Coxinha de Frango' }).getAttribute('aria-checked')).not.toBe(previous);
  });

  it('keeps future seller sections visible without inventing their interface', () => {
    render(<MemoryRouter><CanteenDashboardPage /></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: 'Pedidos Recebidos' }));
    expect(screen.getByText(/será implementada na próxima etapa visual/)).toBeTruthy();
  });

  it('requires confirmation before deleting a product', async () => {
    render(<MemoryRouter><CanteenDashboardPage /></MemoryRouter>);
    expect(await screen.findByText('Coxinha de Frango')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Excluir' }));
    expect(screen.getByRole('alertdialog')).toBeTruthy();
    expect(screen.getByText(/não pode ser desfeita/i)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Excluir produto' }));
    await waitFor(() => expect(screen.queryByText('Coxinha de Frango')).toBeNull());
    expect(screen.getByRole('status').textContent).toContain('excluído com sucesso');
  });
});
