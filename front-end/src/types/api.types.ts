export type EntityId = string;

export type Money = string;

export type ApiErrorDetail = string | ValidationErrorDetail[];

export type ValidationErrorLocation = Array<string | number>;

export interface ValidationErrorDetail {
  loc: ValidationErrorLocation;
  msg: string;
  type: string;
  input?: unknown;
  ctx?: Record<string, string | number | boolean | null>;
}

export interface HTTPValidationError {
  detail: ValidationErrorDetail[];
}

export interface ApiErrorResponse {
  detail: ApiErrorDetail;
}

export interface ApiMessageResponse {
  detail: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
}