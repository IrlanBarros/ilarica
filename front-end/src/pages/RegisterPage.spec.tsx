import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ApiClientError } from '../api/http-error';
import { useAuthStore } from '../store';
import { RegisterPage } from './RegisterPage';

function fillValidForm(): void {
  fireEvent.change(screen.getByLabelText(/nome completo/i), { target: { value: 'Cliente Teste' } });
  fireEvent.change(screen.getByLabelText(/e-mail institucional/i), { target: { value: 'cliente@ufca.edu.br' } });
  fireEvent.change(screen.getByLabelText(/whatsapp/i), { target: { value: '5588999999999' } });
  const [password, passwordConfirmation] = screen.getAllByLabelText(/senha/i);
  fireEvent.change(password, { target: { value: 'Password123' } });
  fireEvent.change(passwordConfirmation, { target: { value: 'Password123' } });
  fireEvent.click(screen.getByRole('checkbox'));
}

describe('RegisterPage', () => {
  const register = vi.fn();

  beforeEach(() => {
    register.mockReset();
    useAuthStore.setState({ isLoading: false, register });
  });

  it('validates password confirmation in the browser without calling the API', () => {
    render(<MemoryRouter><RegisterPage /></MemoryRouter>);
    fillValidForm();
    fireEvent.change(screen.getByLabelText(/confirmar senha/i), { target: { value: 'Different123' } });
    fireEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    expect(screen.getByRole('alert').textContent).toBe('A confirmação deve ser igual à senha.');
    expect(register).not.toHaveBeenCalled();
  });

  it('mirrors password and WhatsApp rules before submitting', () => {
    render(<MemoryRouter><RegisterPage /></MemoryRouter>);
    fireEvent.change(screen.getByLabelText(/nome completo/i), { target: { value: 'Cliente Teste' } });
    fireEvent.change(screen.getByLabelText(/e-mail institucional/i), { target: { value: 'cliente@ufca.edu.br' } });
    fireEvent.change(screen.getByLabelText(/whatsapp/i), { target: { value: '8899999' } });
    const [password, confirmation] = screen.getAllByLabelText(/senha/i);
    fireEvent.change(password, { target: { value: 'senhafraca' } });
    fireEvent.change(confirmation, { target: { value: 'senhafraca' } });
    fireEvent.click(screen.getByRole('button', { name: /cadastrar/i }));
    expect(screen.getByText(/celular válido com DDD/)).toBeTruthy();
    expect(screen.getByText(/letra maiúscula e um número/)).toBeTruthy();
    expect(register).not.toHaveBeenCalled();
  });

  it('sends only the strict API contract fields', async () => {
    register.mockResolvedValue({
      id: 'user-1', name: 'Cliente Teste', email: 'cliente@ufca.edu.br',
      whatsapp: '5588999999999', role: 'customer', is_active: true,
      is_email_validated: false,
    });
    render(<MemoryRouter><RegisterPage /></MemoryRouter>);
    fillValidForm();
    fireEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    await waitFor(() => expect(register).toHaveBeenCalledWith({
      name: 'Cliente Teste', email: 'cliente@ufca.edu.br', whatsapp: '5588999999999',
      password: 'Password123', role: 'customer',
    }));
  });

  it.each([
    [403, 'Este tipo de conta não pode ser criado pelo cadastro público.'],
    [422, 'Revise os dados informados. Use um e-mail institucional da UFCA.'],
  ])('shows a visual message for API status %s', async (status, message) => {
    register.mockRejectedValue(new ApiClientError('API error', status, 'API error'));
    render(<MemoryRouter><RegisterPage /></MemoryRouter>);
    fillValidForm();
    fireEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    await waitFor(() => expect(screen.getByRole('alert').textContent).toBe(message));
  });
});
