import { useEffect, useRef } from 'react';

export function useControlledPolling(callback: () => void | Promise<void>, intervalMs: number): void {
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  useEffect(() => {
    const poll = (): void => {
      if (document.visibilityState === 'visible') void callbackRef.current();
    };
    const timer = window.setInterval(poll, intervalMs);
    document.addEventListener('visibilitychange', poll);
    return () => {
      window.clearInterval(timer);
      document.removeEventListener('visibilitychange', poll);
    };
  }, [intervalMs]);
}
