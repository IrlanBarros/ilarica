export function redirectToLogin(): void {
  if (typeof window === 'undefined') {
    return;
  }

  if (window.location.pathname === '/login') {
    return;
  }

  window.location.assign('/login');
}