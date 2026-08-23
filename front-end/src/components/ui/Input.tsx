import { forwardRef, useId } from 'react';
import type { ComponentPropsWithoutRef } from 'react';

import { cn } from '../../lib/utils';

interface InputProps extends ComponentPropsWithoutRef<'input'> {
  label?: string;
  error?: string;
  wrapperClassName?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { id, label, error, className, wrapperClassName, required, 'aria-describedby': ariaDescribedBy, ...props },
  ref,
): React.JSX.Element {
  const generatedId = useId();
  const inputId = id ?? generatedId;
  const errorId = `${inputId}-error`;
  const describedBy = [ariaDescribedBy, error ? errorId : undefined].filter(Boolean).join(' ') || undefined;

  return (
    <div className={cn('w-full', wrapperClassName)}>
      {label ? (
        <label htmlFor={inputId} className="mb-1.5 block text-sm font-medium text-slate-700">
          {label}
          {required ? <span className="ml-1 text-red-600">*</span> : null}
        </label>
      ) : null}

      <input
        id={inputId}
        ref={ref}
        className={cn(
          'h-10 w-full rounded-xl border border-slate-300 bg-white px-3 text-sm text-slate-900',
          'placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500',
          'disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500',
          error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
          className,
        )}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        required={required}
        {...props}
      />

      {error ? (
        <p id={errorId} className="mt-1 text-sm text-red-600" role="alert" aria-live="assertive">
          {error}
        </p>
      ) : null}
    </div>
  );
});

export type { InputProps };