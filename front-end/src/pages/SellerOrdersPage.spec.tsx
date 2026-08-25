import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { useSellerStore } from '../store';
import { SellerOrdersPage } from './SellerOrdersPage';

describe('SellerOrdersPage', () => {
  beforeEach(() => useSellerStore.getState().resetOrders());

  it('organizes received orders by operational stage', () => {
    render(<MemoryRouter><SellerOrdersPage /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: 'Pedidos Recebidos' })).toBeTruthy();
    expect(screen.getByText('Pedido #4081')).toBeTruthy();
    fireEvent.click(screen.getByRole('tab', { name: /Em preparo/ }));
    expect(screen.getByText('Pedido #4079')).toBeTruthy();
    expect(screen.queryByText('Pedido #4081')).toBeNull();
  });

  it('moves a new order to preparation without changing server-owned totals', () => {
    render(<MemoryRouter><SellerOrdersPage /></MemoryRouter>);
    fireEvent.click(screen.getAllByRole('button', { name: 'Aceitar pedido' })[0]);
    expect(screen.queryByText('Pedido #4081')).toBeNull();
    fireEvent.click(screen.getByRole('tab', { name: /Em preparo/ }));
    expect(screen.getByText('Pedido #4081')).toBeTruthy();
    expect(screen.getByText(/18,00/)).toBeTruthy();
  });
});
