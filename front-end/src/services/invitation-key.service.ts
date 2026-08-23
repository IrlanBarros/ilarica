import { apiClient } from '../api';
import type {
  ApiMessageResponse,
  InvitationKey,
  InvitationKeyCreate,
  InvitationKeyUpdate,
} from '../types';

export async function listInvitationKeys(): Promise<InvitationKey[]> {
  const response = await apiClient.get<InvitationKey[]>('/invitation-keys/');
  return response.data;
}

export async function getInvitationKey(keyId: string): Promise<InvitationKey> {
  const response = await apiClient.get<InvitationKey>(`/invitation-keys/${keyId}`);
  return response.data;
}

export async function createInvitationKey(payload: InvitationKeyCreate): Promise<InvitationKey> {
  const response = await apiClient.post<InvitationKey>('/invitation-keys/', payload);
  return response.data;
}

export async function updateInvitationKey(keyId: string, payload: InvitationKeyUpdate): Promise<InvitationKey> {
  const response = await apiClient.patch<InvitationKey>(`/invitation-keys/${keyId}`, payload);
  return response.data;
}

export async function deleteInvitationKey(keyId: string): Promise<ApiMessageResponse> {
  const response = await apiClient.delete<ApiMessageResponse>(`/invitation-keys/${keyId}`);
  return response.data;
}