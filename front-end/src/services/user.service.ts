import { apiClient } from '../api';
import type { User } from '../types';

export async function getMe(): Promise<User> {
  const response = await apiClient.get<User>('/users/me');

  return response.data;
}

export const getMyProfile = getMe;