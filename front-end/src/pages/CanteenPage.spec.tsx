import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useCartStore } from '../store';
import type { Canteen, Product } from '../types';
import { CanteenPage } from './CanteenPage';

const { getCanteenMock, listProductsMock } = vi.hoisted(() => ({
  getCanteenMock: vi.fn(),
  listProductsMock: vi.fn(),
}));

vi.mock('../services/canteen.service', () => ({ getCanteen: getCanteenMock }));
vi.mock('../services/product.service', () => ({ listProducts: listProductsMock }));

const canteen: Canteen = {
  id: 'canteen-1',
  user_id: 'staff-1',
  name: 'Doces da Júlia',
  location: 'Centro de Convivência',
  is_open: true,
  is_accepting_orders: true,
  products: ['product-1'],
};

const product: Product = {
  id: 'product-1',
  canteen_id: 'canteen-1',
  name: 'Brownie tradicional',
  description: 'Macio e recheado com chocolate.',
  price: '5.00',
  is_active: true,
  is_fast_stock_enabled: false,
  category: 'doces',
  stock_quantity: 12,
};

function renderPage(): void {
  render(
    <MemoryRouter initialEntries={['/cantina/canteen-1']}>
      <Routes>
        <Route path="/cantina/:id" element={<CanteenPage />} />
        <Route path="/carrinho" element={<p>Carrinho</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('CanteenPage', () => {
  beforeEach(() => {
    getCanteenMock.mockReset();
    listProductsMock.mockReset();
    useCartStore.getState().clearCart();
  });

  it('renders the real canteen and only its active products', async () => {
    getCanteenMock.mockResolvedValue(canteen);
    listProductsMock.mockResolvedValue([
      product,
      { ...product, id: 'inactive', name: 'Inativo', is_active: false },
      { ...product, id: 'other', canteen_id: 'canteen-2', name: 'Outra cantina' },
    ]);
    renderPage();

    expect(screen.getByLabelText('Carregando cardápio')).toBeTruthy();
    expect(await screen.findByRole('heading', { name: 'Doces da Júlia' })).toBeTruthy();
    expect(screen.getByText(/Centro de Convivência/)).toBeTruthy();
    expect(screen.getByText('Brownie tradicional')).toBeTruthy();
    expect(screen.queryByText('Inativo')).toBeNull();
    expect(screen.queryByText('Outra cantina')).toBeNull();
  });

  it('adds products to Zustand and updates the sticky cart summary', async () => {
    getCanteenMock.mockResolvedValue(canteen);
    listProductsMock.mockResolvedValue([product]);
    renderPage();
    await screen.findByText('Brownie tradicional');

    fireEvent.click(screen.getByRole('button', { name: 'Ver detalhes de Brownie tradicional' }));
    expect(screen.getByText('Quantidade disponível: 12')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Aumentar quantidade' }));
    fireEvent.click(screen.getByRole('button', { name: 'Adicionar 2 ao carrinho' }));

    expect(screen.getByText('2 itens selecionados')).toBeTruthy();
    expect(screen.getByText('R$ 10,00 subtotal')).toBeTruthy();
    expect(useCartStore.getState().items[0].quantity).toBe(2);
    fireEvent.click(screen.getByRole('link', { name: /Ver Carrinho/ }));
    expect(screen.getByText('Carrinho')).toBeTruthy();
  });

  it('preserves a cart from another canteen and explains the conflict', async () => {
    useCartStore.getState().addItem({ ...product, id: 'other-product', canteen_id: 'canteen-2' });
    getCanteenMock.mockResolvedValue(canteen);
    listProductsMock.mockResolvedValue([product]);
    renderPage();
    await screen.findByText('Brownie tradicional');

    fireEvent.click(screen.getByRole('button', { name: 'Ver detalhes de Brownie tradicional' }));
    fireEvent.click(screen.getByRole('button', { name: 'Adicionar 1 ao carrinho' }));

    expect(screen.getByRole('status').textContent).toContain('outra cantina');
    expect(useCartStore.getState().items).toHaveLength(1);
    expect(useCartStore.getState().canteenId).toBe('canteen-2');
  });

  it('filters products by category', async () => {
    getCanteenMock.mockResolvedValue(canteen);
    listProductsMock.mockResolvedValue([
      product,
      { ...product, id: 'juice', name: 'Suco', category: 'bebidas' },
    ]);
    renderPage();
    await screen.findByText('Brownie tradicional');

    fireEvent.click(screen.getByRole('button', { name: 'Bebidas' }));

    expect(screen.getByText('Suco')).toBeTruthy();
    expect(screen.queryByText('Brownie tradicional')).toBeNull();
  });

  it('shows the next opening and prevents adding outside business hours', async () => {
    getCanteenMock.mockResolvedValue({
      ...canteen,
      is_accepting_orders: false,
      next_opening_at: '2026-08-26T08:00:00-03:00',
    });
    listProductsMock.mockResolvedValue([product]);
    renderPage();

    await screen.findByText('Fechado no momento', { exact: false });
    expect(screen.getByText(/Próxima abertura/)).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Ver detalhes de Brownie tradicional' })).toHaveProperty('disabled', true);
  });

  it('shows an error and retries the API requests', async () => {
    getCanteenMock.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(canteen);
    listProductsMock.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce([product]);
    renderPage();

    expect((await screen.findByRole('alert')).textContent).toContain('Não foi possível carregar');
    fireEvent.click(screen.getByRole('button', { name: 'Tentar novamente' }));

    await waitFor(() => expect(screen.getByText('Brownie tradicional')).toBeTruthy());
    expect(getCanteenMock).toHaveBeenCalledTimes(2);
    expect(listProductsMock).toHaveBeenCalledTimes(2);
  });
});
