import { afterEach, beforeEach, vi } from 'vitest';

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState({}, '', '/');
});

afterEach(() => {
  window.localStorage.clear();
  vi.restoreAllMocks();
});