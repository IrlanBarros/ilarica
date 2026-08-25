import { forwardRef, useId } from 'react';
import type { ComponentPropsWithoutRef, ReactNode } from 'react';

import { cn } from '../../lib/utils';

interface InputProps extends Omit<ComponentPropsWithoutRef<'input'>, 'prefix'> {
  label?: string;
  error?: string;
  wrapperClassName?: string;
  prefix?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { id, label, error, className, wrapperClassName, prefix, required, 'aria-describedby': ariaDescribedBy, ...props },
  ref,
): React.JSX.Element {
  const generatedId = useId();
  const inputId = id ?? generatedId;
  const errorId = `${inputId}-error`;
  const describedBy = [ariaDescribedBy, error ? errorId : undefined].filter(Boolean).join(' ') || undefined;

  return (
    <div className={cn('w-full', wrapperClassName)}>
      {label ? (
        <label htmlFor={inputId} className="mb-2 block text-[13px] font-bold text-ilarica-muted">
          {label}
        </label>
      ) : null}

      <div className="relative">
        {prefix ? <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center border-r border-slate-200 px-3 text-sm font-semibold text-slate-600" aria-hidden="true">{prefix}</span> : null}
        <input
          id={inputId}
          ref={ref}
          className={cn(
            'h-10 w-full rounded-xl border border-slate-300 bg-white px-3 text-sm text-slate-900',
            'placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500',
            'disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500',
            prefix && 'pl-16',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
            className,
          )}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          required={required}
          {...props}
        />
      </div>

      {error ? (
        <p id={errorId} className="mt-1 text-sm text-red-600" role="alert" aria-live="assertive">
          {error}
        </p>
      ) : null}
    </div>
  );
});

export type { InputProps };
