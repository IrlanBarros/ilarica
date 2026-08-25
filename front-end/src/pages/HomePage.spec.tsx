import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useAuthStore, useCartStore } from '../store';
import type { Canteen, Product } from '../types';
import { HomePage } from './HomePage';

const { listCanteensMock, listProductsMock } = vi.hoisted(() => ({
  listCanteensMock: vi.fn(),
  listProductsMock: vi.fn(),
}));

vi.mock('../services/canteen.service', () => ({ listCanteens: listCanteensMock }));
vi.mock('../services/product.service', () => ({ listProducts: listProductsMock }));

const canteens: Canteen[] = [
  {
    id: 'canteen-1',
    user_id: 'staff-1',
    name: 'Cantina do Bloco B',
    location: 'Bloco B',
    is_open: true,
    products: [],
  },
  {
    id: 'canteen-2',
    user_id: 'staff-2',
    name: 'Marmitas da Tia Cleide',
    location: 'Biblioteca Central',
    is_open: false,
    products: [],
  },
];

const products: Product[] = [
  {
    id: 'product-1',
    canteen_id: 'canteen-1',
    name: 'Coxinha de frango',
    description: null,
    price: '7.00',
    is_active: true,
    is_fast_stock_enabled: false,
  },
];

function renderHome(): void {
  render(
    <MemoryRouter>
      <HomePage />
    </MemoryRouter>,
  );
}

describe('HomePage', () => {
  beforeEach(() => {
    listCanteensMock.mockReset();
    listProductsMock.mockReset();
    useAuthStore.setState({
      user: {
        id: 'customer-1',
        name: 'Matheus Silva',
        email: 'matheus@aluno.ufca.edu.br',
        whatsapp: '5588999999999',
        role: 'customer',
        is_active: true,
        is_email_validated: true,
      },
    });
    useCartStore.getState().clearCart();
  });

  it('renders API canteens, products and the authenticated first name', async () => {
    listCanteensMock.mockResolvedValue(canteens);
    listProductsMock.mockResolvedValue(products);
    renderHome();

    expect(screen.getByLabelText('Carregando vendedores')).toBeTruthy();
    expect(await screen.findByText('Olá, Matheus!')).toBeTruthy();
    expect(screen.getByText('Cantina do Bloco B')).toBeTruthy();
    expect(screen.getByText('Bloco B')).toBeTruthy();
    expect(screen.getByText('Marmitas da Tia Cleide')).toBeTruthy();
    expect(screen.getByText('Biblioteca Central')).toBeTruthy();
    expect(screen.getByText('Fechado')).toBeTruthy();
  });

  it('filters sellers by their product names', async () => {
    listCanteensMock.mockResolvedValue(canteens);
    listProductsMock.mockResolvedValue(products);
    renderHome();
    await screen.findByText('Cantina do Bloco B');

    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'coxinha' } });
    expect(screen.getByText('Cantina do Bloco B')).toBeTruthy();
    expect(screen.queryByText('Marmitas da Tia Cleide')).toBeNull();

    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'pizza' } });
    expect(screen.getByText('Nenhum vendedor encontrado')).toBeTruthy();
  });

  it('shows an empty state when the API has no sellers', async () => {
    listCanteensMock.mockResolvedValue([]);
    listProductsMock.mockResolvedValue([]);
    renderHome();

    expect(await screen.findByText('Nenhum vendedor disponível agora')).toBeTruthy();
  });

  it('uses only neutral protection when an unexpected invalid API item escapes', async () => {
    listCanteensMock.mockResolvedValue([{ ...canteens[0], name: '', location: '' }]);
    listProductsMock.mockResolvedValue([]);
    renderHome();

    expect(await screen.findByText('Vendedor indisponível')).toBeTruthy();
    expect(screen.getByText('Local não informado')).toBeTruthy();
  });

  it('shows an error and retries both API requests', async () => {
    listCanteensMock.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(canteens);
    listProductsMock.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(products);
    renderHome();

    expect((await screen.findByRole('alert')).textContent).toContain(
      'Não foi possível carregar os vendedores agora.',
    );
    fireEvent.click(screen.getByRole('button', { name: 'Tentar novamente' }));

    await waitFor(() => expect(screen.getByText('Cantina do Bloco B')).toBeTruthy());
    expect(listCanteensMock).toHaveBeenCalledTimes(2);
    expect(listProductsMock).toHaveBeenCalledTimes(2);
  });
});
