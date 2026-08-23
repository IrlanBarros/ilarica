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