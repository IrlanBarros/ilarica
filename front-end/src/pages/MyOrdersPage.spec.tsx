import { render, screen } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
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
      total_amount: '15.00', destination: null, canteen: { id: 'canteen-1', name: 'Cantina Central', location: 'Bloco H' }, pickup_pin: '4821',
    }]);
    render(<MyOrdersPage />);
    expect(await screen.findByText('Cantina Central')).toBeTruthy();
    expect(screen.getByText('Pronto para retirada')).toBeTruthy();
    expect(screen.getByText('4821')).toBeTruthy();
  });

  it('renders an empty state when the customer has no orders', async () => {
    mock.onGet('/orders/me').reply(200, []);
    render(<MyOrdersPage />);
    expect(await screen.findByText('Você ainda não fez nenhum pedido.')).toBeTruthy();
  });
});
