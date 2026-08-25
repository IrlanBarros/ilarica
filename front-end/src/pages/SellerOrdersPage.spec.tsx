import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { useSellerStore } from '../store';
import type { SellerOrder } from '../types';
import { SellerOrdersPage } from './SellerOrdersPage';

const orders: SellerOrder[] = [
  {
    id: '40810000-0000-4000-8000-000000000001', canteen_id: '10000000-0000-4000-8000-000000000001', status: 'paid', total_amount: '18.00',
    customer: { id: '20000000-0000-4000-8000-000000000001', name: 'Ana Clara' },
    fulfillment_type: 'delivery',
    destination: { id: '30000000-0000-4000-8000-000000000001', name: 'Bloco C', description: 'Sala 204' },
    items: [{ id: '50000000-0000-4000-8000-000000000001', product_id: '60000000-0000-4000-8000-000000000001', name: 'Coxinha', quantity: 2, unit_price: '9.00' }],
  },
  {
    id: '40790000-0000-4000-8000-000000000001', canteen_id: '10000000-0000-4000-8000-000000000001', status: 'preparing', total_amount: '13.50',
    customer: { id: '20000000-0000-4000-8000-000000000002', name: 'Marina Alves' },
    fulfillment_type: 'delivery',
    destination: { id: '30000000-0000-4000-8000-000000000002', name: 'Bloco A', description: null },
    items: [{ id: '50000000-0000-4000-8000-000000000002', product_id: '60000000-0000-4000-8000-000000000002', name: 'Pastel', quantity: 1, unit_price: '13.50' }],
  },
];

describe('SellerOrdersPage', () => {
  beforeEach(() => useSellerStore.setState({
    orders,
    orderStage: 'new',
    isOrdersLoading: false,
    ordersError: null,
    transitioningOrderId: null,
    confirmingOrderId: null,
    loadOrders: async () => undefined,
    advanceOrder: async (orderId) => useSellerStore.setState((state) => ({
      orders: state.orders.map((order) => order.id === orderId ? { ...order, status: 'preparing' } : order),
    })),
    confirmPickup: async (orderId) => useSellerStore.setState((state) => ({ orders: state.orders.filter((order) => order.id !== orderId) })),
  }));

  it('organizes server orders by operational stage', () => {
    render(<MemoryRouter><SellerOrdersPage /></MemoryRouter>);
    expect(screen.getByText('Pedido #40810000')).toBeTruthy();
    fireEvent.click(screen.getByRole('tab', { name: /Em preparo/ }));
    expect(screen.getByText('Pedido #40790000')).toBeTruthy();
    expect(screen.queryByText('Pedido #40810000')).toBeNull();
  });

  it('moves an order only after the server action resolves', async () => {
    render(<MemoryRouter><SellerOrdersPage /></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: 'Aceitar pedido' }));
    await waitFor(() => expect(screen.queryByText('Pedido #40810000')).toBeNull());
    fireEvent.click(screen.getByRole('tab', { name: /Em preparo/ }));
    expect(screen.getByText('Pedido #40810000')).toBeTruthy();
    expect(screen.getByText(/18,00/)).toBeTruthy();
  });

  it('renders loading and error feedback', () => {
    act(() => useSellerStore.setState({ isOrdersLoading: true, orders: [] }));
    const view = render(<MemoryRouter><SellerOrdersPage /></MemoryRouter>);
    expect(screen.getByText('Carregando pedidos...')).toBeTruthy();

    act(() => useSellerStore.setState({ isOrdersLoading: false, ordersError: 'Falha segura', orders: [] }));
    view.rerender(<MemoryRouter><SellerOrdersPage /></MemoryRouter>);
    expect(screen.getByRole('alert').textContent).toContain('Falha segura');
  });

  it('validates a four-digit PIN and removes a completed pickup from the active queue', async () => {
    const ready: SellerOrder = { ...orders[0], status: 'ready_for_pickup', fulfillment_type: 'pickup', destination: null };
    useSellerStore.setState({ orders: [ready], orderStage: 'ready' });
    render(<MemoryRouter><SellerOrdersPage /></MemoryRouter>);

    const input = screen.getByRole('textbox', { name: 'PIN do pedido 40810000' });
    fireEvent.change(input, { target: { value: '4821' } });
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar retirada' }));

    await waitFor(() => expect(screen.queryByText('Pedido #40810000')).toBeNull());
    expect(screen.getByText('Nenhum pedido nesta etapa')).toBeTruthy();
  });
});
