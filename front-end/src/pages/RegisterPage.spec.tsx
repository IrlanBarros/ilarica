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
    fireEvent.change(screen.getByLabelText(/confirmação de senha/i), { target: { value: 'Different123' } });
    fireEvent.click(screen.getByRole('button', { name: /criar conta/i }));

    expect(screen.getByRole('alert').textContent).toBe('A confirmação de senha deve ser igual à senha.');
    expect(register).not.toHaveBeenCalled();
  });

  it.each([
    [403, 'Este tipo de conta não pode ser criado pelo cadastro público.'],
    [422, 'Revise os dados informados. Use um e-mail institucional da UFCA.'],
  ])('shows a visual message for API status %s', async (status, message) => {
    register.mockRejectedValue(new ApiClientError('API error', status, 'API error'));
    render(<MemoryRouter><RegisterPage /></MemoryRouter>);
    fillValidForm();
    fireEvent.click(screen.getByRole('button', { name: /criar conta/i }));

    await waitFor(() => expect(screen.getByRole('alert').textContent).toBe(message));
  });
});
