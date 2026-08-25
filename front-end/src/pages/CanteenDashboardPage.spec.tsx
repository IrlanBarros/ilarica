import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { useSellerStore } from '../store';
import { CanteenDashboardPage } from './CanteenDashboardPage';

describe('CanteenDashboardPage', () => {
  beforeEach(() => useSellerStore.setState({ activeSection: 'menu' }));

  it('renders the seller menu mock and handles visual availability state', () => {
    render(<MemoryRouter><CanteenDashboardPage /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: 'Meu Cardápio' })).toBeTruthy();
    expect(screen.getByText('Coxinha de Frango')).toBeTruthy();
    expect(screen.getByText('Horário de Funcionamento')).toBeTruthy();

    const availability = screen.getByRole('switch', { name: 'Alterar disponibilidade de Coxinha de Frango' });
    const previous = availability.getAttribute('aria-checked');
    fireEvent.click(availability);
    expect(availability.getAttribute('aria-checked')).not.toBe(previous);
  });

  it('keeps future seller sections visible without inventing their interface', () => {
    render(<MemoryRouter><CanteenDashboardPage /></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: 'Pedidos Recebidos' }));
    expect(screen.getByText(/será implementada na próxima etapa visual/)).toBeTruthy();
  });
});
