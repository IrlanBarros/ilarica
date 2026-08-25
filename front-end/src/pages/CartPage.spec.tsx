import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { useAuthStore, useCartStore } from '../store';
import type { Product } from '../types';
import { CartPage } from './CartPage';

const product: Product = {
  id: 'product-1',
  canteen_id: 'canteen-1',
  name: 'Coxinha Suprema de Frango',
  description: null,
  price: '6.50',
  is_active: true,
  is_fast_stock_enabled: false,
  category: 'salgados',
  stock_quantity: 20,
};

function renderCart(): void {
  render(
    <MemoryRouter>
      <Routes>
        <Route path="/" element={<CartPage />} />
        <Route path="/checkout" element={<p>Checkout</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('CartPage', () => {
  beforeEach(() => {
    useCartStore.getState().clearCart();
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
  });

  it('renders an empty state with a route back to the Mural', () => {
    renderCart();

    expect(screen.getByRole('heading', { name: 'Seu carrinho está vazio' })).toBeTruthy();
    expect(screen.getByRole('link', { name: 'Voltar ao Mural' }).getAttribute('href')).toBe('/');
  });

  it('increases, decreases and removes item quantities with live totals', () => {
    useCartStore.getState().addItem(product, 2);
    renderCart();

    expect(screen.getAllByText('R$ 13,00')).toHaveLength(2);
    expect(screen.getByText('R$ 14,00')).toBeTruthy();

    fireEvent.click(screen.getByRole('button', { name: 'Aumentar Coxinha Suprema de Frango' }));
    expect(screen.getByLabelText('Quantidade de Coxinha Suprema de Frango').textContent).toBe('3');
    expect(screen.getAllByText('R$ 19,50')).toHaveLength(2);

    fireEvent.click(screen.getByRole('button', { name: 'Diminuir Coxinha Suprema de Frango' }));
    expect(screen.getByLabelText('Quantidade de Coxinha Suprema de Frango').textContent).toBe('2');

    fireEvent.click(screen.getAllByRole('button', { name: 'Remover' })[0]);
    expect(screen.getByRole('heading', { name: 'Seu carrinho está vazio' })).toBeTruthy();
  });

  it('recalculates delivery and tip selections without starting checkout', () => {
    useCartStore.getState().addItem(product);
    renderCart();

    expect(screen.getByText('R$ 7,50')).toBeTruthy();
    fireEvent.click(screen.getByRole('switch', { name: 'Retirar pessoalmente' }));
    expect(screen.getByText('R$ 9,50')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /3,00/ }));
    expect(screen.getByText('R$ 11,50')).toBeTruthy();

    fireEvent.click(screen.getByRole('button', { name: 'Finalizar Pedido' }));
    expect(screen.getByText('Checkout')).toBeTruthy();
  });

  it('clears the cart through an explicit action', () => {
    useCartStore.getState().addItem(product);
    renderCart();

    fireEvent.click(screen.getByRole('button', { name: 'Limpar carrinho' }));
    expect(useCartStore.getState().items).toHaveLength(0);
    expect(screen.getByRole('heading', { name: 'Seu carrinho está vazio' })).toBeTruthy();
  });
});
