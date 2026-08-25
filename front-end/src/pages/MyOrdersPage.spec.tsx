import { render, screen } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { apiClient } from '../api';
import { MyOrdersPage } from './MyOrdersPage';

describe('MyOrdersPage', () => {
  let mock: MockAdapter;
  beforeEach(() => { mock = new MockAdapter(apiClient); });

  it('renders authenticated pickup tracking and its PIN', async () => {
    mock.onGet('/orders/me').reply(200, [{
      id: 'order-12345678', canteen_id: 'canteen-1', status: 'ready_for_pickup', fulfillment_type: 'pickup',
      items: [{ id: 'item-1', product_id: 'product-1', name: 'Coxinha', quantity: 2, unit_price: '7.50' }],
      total_amount: '15.00', destination: null, location_details: null, canteen: { id: 'canteen-1', name: 'Cantina Central', location: 'Bloco H' }, pickup_pin: '4821',
    }]);
    render(<MemoryRouter><MyOrdersPage /></MemoryRouter>);
    expect(await screen.findByText('Cantina Central')).toBeTruthy();
    expect(screen.getByText('Pronto para retirada')).toBeTruthy();
    expect(screen.getByText('4821')).toBeTruthy();
  });

  it('renders the macro zone combined with the free-form detail for deliveries', async () => {
    mock.onGet('/orders/me').reply(200, [{
      id: 'order-99999999', canteen_id: 'canteen-1', status: 'paid', fulfillment_type: 'delivery',
      items: [{ id: 'item-1', product_id: 'product-1', name: 'Pastel', quantity: 1, unit_price: '9.50' }],
      total_amount: '9.50', destination: { id: 'zone-1', name: 'Bloco H', description: null }, location_details: 'Sala 12', canteen: { id: 'canteen-1', name: 'Cantina Central', location: 'Bloco H' }, pickup_pin: null,
    }]);
    render(<MemoryRouter><MyOrdersPage /></MemoryRouter>);
    expect(await screen.findByText('Bloco H - Sala 12')).toBeTruthy();
  });

  it('renders an empty state when the customer has no orders', async () => {
    mock.onGet('/orders/me').reply(200, []);
    render(<MemoryRouter><MyOrdersPage /></MemoryRouter>);
    expect(await screen.findByText('Você ainda não fez nenhum pedido')).toBeTruthy();
  });
});
