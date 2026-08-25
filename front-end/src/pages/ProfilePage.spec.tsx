import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useAuthStore } from '../store';
import { ProfilePage } from './ProfilePage';

describe('ProfilePage', () => {
  beforeEach(() => useAuthStore.setState({ user: { id: 'user-id', name: 'Ana Clara', email: 'ana@aluno.ufca.edu.br', whatsapp: '5588999999999', role: 'customer', is_active: true, is_email_validated: true }, isAuthenticated: true }));

  it('shows the authenticated Zustand profile and logs out', () => {
    const logout = vi.fn();
    useAuthStore.setState({ logout });
    render(<MemoryRouter><ProfilePage /></MemoryRouter>);
    expect(screen.getByDisplayValue('Ana Clara')).toBeTruthy();
    expect(screen.getByDisplayValue('ana@aluno.ufca.edu.br')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Sair da conta' }));
    fireEvent.click(screen.getByRole('button', { name: /^Sair$/ }));
    expect(logout).toHaveBeenCalledOnce();
  });
});
