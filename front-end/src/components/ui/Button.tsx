import type { ComponentPropsWithoutRef, ReactNode } from 'react';

import { cn } from '../../lib/utils';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ComponentPropsWithoutRef<'button'> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  loadingText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-orange-600 text-white hover:bg-orange-500 focus-visible:ring-orange-500',
  secondary: 'bg-slate-200 text-slate-900 hover:bg-slate-300 focus-visible:ring-slate-400',
  danger: 'bg-red-600 text-white hover:bg-red-500 focus-visible:ring-red-500',
  ghost: 'bg-transparent text-slate-700 hover:bg-slate-100 focus-visible:ring-slate-300',
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'h-9 px-3 text-sm',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-base',
};

export function Button({
  className,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  loadingText,
  disabled,
  children,
  leftIcon,
  rightIcon,
  type = 'button',
  ...props
}: ButtonProps): React.JSX.Element {
  const isDisabled = disabled || isLoading;

  return (
    <button
      type={type}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
        'disabled:cursor-not-allowed disabled:opacity-60',
        variantClasses[variant],
        sizeClasses[size],
        className,
      )}
      disabled={isDisabled}
      aria-busy={isLoading}
      aria-live="polite"
      {...props}
    >
      {isLoading ? (
        <>
          <span
            className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
            aria-hidden="true"
          />
          <span>{loadingText ?? 'Carregando...'}</span>
        </>
      ) : (
        <>
          {leftIcon}
          <span>{children}</span>
          {rightIcon}
        </>
      )}
    </button>
  );
}

export type { ButtonProps, ButtonSize, ButtonVariant };