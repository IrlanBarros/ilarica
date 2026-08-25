import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { VerifyEmailPage } from './VerifyEmailPage';

const { confirmMock } = vi.hoisted(() => ({ confirmMock: vi.fn() }));

vi.mock('../services/auth.service', () => ({
  confirmEmailVerification: confirmMock,
  requestEmailVerification: vi.fn(),
}));

describe('VerifyEmailPage', () => {
  beforeEach(() => confirmMock.mockReset());

  it('confirms the single-use token and offers the login link', async () => {
    confirmMock.mockResolvedValue(undefined);
    render(<MemoryRouter initialEntries={['/verificar-email?token=secure-token']}><VerifyEmailPage /></MemoryRouter>);

    expect(screen.getByLabelText('Validando e-mail')).toBeTruthy();
    await waitFor(() => expect(confirmMock).toHaveBeenCalledWith('secure-token'));
    expect(await screen.findByText('E-mail confirmado')).toBeTruthy();
    expect(screen.getByRole('link', { name: 'Ir para o login' })).toBeTruthy();
  });

  it('shows a friendly message for an expired link', async () => {
    confirmMock.mockRejectedValue(new Error('expired'));
    render(<MemoryRouter initialEntries={['/verificar-email?token=expired-token']}><VerifyEmailPage /></MemoryRouter>);

    expect(await screen.findByText(/inválido, expirou ou já foi utilizado/)).toBeTruthy();
  });
});
