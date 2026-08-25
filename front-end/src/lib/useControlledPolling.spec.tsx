import { render } from '@testing-library/react';
import { useState } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { useControlledPolling } from './useControlledPolling';

function Probe({ callback }: { callback: () => void }): React.JSX.Element {
  const [interval] = useState(1_000);
  useControlledPolling(callback, interval);
  return <div />;
}

describe('useControlledPolling', () => {
  afterEach(() => vi.useRealTimers());

  it('polls while visible and stops after unmount', () => {
    vi.useFakeTimers();
    const callback = vi.fn();
    const view = render(<Probe callback={callback} />);
    vi.advanceTimersByTime(2_000);
    expect(callback).toHaveBeenCalledTimes(2);
    view.unmount();
    vi.advanceTimersByTime(2_000);
    expect(callback).toHaveBeenCalledTimes(2);
  });
});
