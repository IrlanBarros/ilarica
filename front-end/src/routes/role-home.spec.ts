import { describe, expect, it } from 'vitest';

import { getRoleHome } from './role-home';

describe('getRoleHome', () => {
  it.each([
    ['customer', '/'],
    ['courier', '/entregas'],
    ['canteen_staff', '/vendedor/pedidos'],
    ['admin', '/admin'],
  ] as const)('maps %s to %s', (role, destination) => {
    expect(getRoleHome(role)).toBe(destination);
  });
});
