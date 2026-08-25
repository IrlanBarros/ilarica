import { isAxiosError } from 'axios';

import type { ApiErrorResponse, ValidationErrorDetail } from '../types';

export class ApiClientError extends Error {
  readonly status: number | null;
  readonly details: string | ValidationErrorDetail[] | null;

  constructor(message: string, status: number | null, details: string | ValidationErrorDetail[] | null) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.details = details;
  }
}

export function normalizeApiError(error: unknown): ApiClientError {
  if (error instanceof ApiClientError) {
    return error;
  }

  if (isAxiosError(error)) {
    const status = error.response?.status ?? null;
    const data = error.response?.data as ApiErrorResponse | undefined;
    const detail = data?.detail ?? null;
    const message =
      typeof detail === 'string'
        ? detail
        : error.message || 'An unexpected API error occurred.';

    return new ApiClientError(message, status, detail);
  }

  if (error instanceof Error) {
    return new ApiClientError(error.message, null, null);
  }

  return new ApiClientError('An unexpected API error occurred.', null, null);
}

export function friendlyApiMessage(error: unknown, fallback = 'Não foi possível concluir a operação. Tente novamente.'): string {
  const normalized = normalizeApiError(error);
  const message = normalized.message.toLowerCase();
  if (normalized.status === 401) return 'Sua sessão expirou. Entre novamente para continuar.';
  if (normalized.status === 403) return 'Você não tem permissão para realizar esta ação.';
  if (normalized.status === 404) return 'O conteúdo solicitado não foi encontrado.';
  if (normalized.status === 422 || normalized.status === 400) return 'Revise os dados informados e tente novamente.';
  if (message.includes('saldo') || message.includes('balance')) return 'Saldo insuficiente para concluir o pagamento.';
  if (message.includes('unavailable') || message.includes('indispon')) return 'Um dos itens não está mais disponível.';
  if (message.includes('already paid')) return 'Este pedido já foi pago.';
  if (message.includes('expired') || message.includes('expir')) return 'Este pagamento expirou. Gere uma nova cobrança.';
  if (normalized.status !== null && normalized.status >= 500) return 'O serviço está temporariamente indisponível. Tente novamente em instantes.';
  return fallback;
}
