import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ApiClientError } from '../api/http-error';
import { useAuthStore } from '../store';
import { LoginPage } from './LoginPage';

function renderLogin(initialEntry: string | { pathname: string; state: unknown } = '/login'): void {
  render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/entregas" element={<p>Mural do entregador</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('LoginPage', () => {
  const login = vi.fn();

  beforeEach(() => {
    login.mockReset();
    useAuthStore.setState({ user: null, isLoading: false, login });
  });

  it('redirects to the authenticated role home', async () => {
    login.mockResolvedValue({
      id: 'courier-1', name: 'Entregador', email: 'courier@aluno.ufca.edu.br',
      whatsapp: '5588999999999', role: 'courier', is_active: true,
      is_email_validated: false,
    });
    renderLogin();
    fireEvent.change(screen.getByLabelText(/e-mail institucional/i), { target: { value: 'courier@aluno.ufca.edu.br' } });
    fireEvent.change(screen.getByLabelText('Senha'), { target: { value: 'Password123' } });
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => expect(screen.getByText('Mural do entregador')).toBeTruthy());
  });

  it('shows an invalid credentials message for 401', async () => {
    login.mockRejectedValue(new ApiClientError('Unauthorized', 401, 'Unauthorized'));
    renderLogin();
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => expect(screen.getByRole('alert').textContent).toBe('E-mail ou senha incorretos.'));
  });

  it('shows registration success feedback', () => {
    renderLogin({ pathname: '/login', state: { registered: true } });
    expect(screen.getByRole('status').textContent).toContain('Cadastro concluído com sucesso');
  });
});
