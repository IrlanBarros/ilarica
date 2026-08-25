import type { ComponentPropsWithoutRef } from 'react';

import { cn } from '../../lib/utils';

function Card({ className, ...props }: ComponentPropsWithoutRef<'section'>): React.JSX.Element {
  return (
    <section
      className={cn('rounded-2xl border border-slate-200 bg-white shadow-sm', className)}
      {...props}
    />
  );
}

function CardHeader({ className, ...props }: ComponentPropsWithoutRef<'header'>): React.JSX.Element {
  return <header className={cn('border-b border-slate-100 p-5', className)} {...props} />;
}

function CardTitle({ className, ...props }: ComponentPropsWithoutRef<'h3'>): React.JSX.Element {
  return <h3 className={cn('text-lg font-semibold text-slate-900', className)} {...props} />;
}

function CardContent({ className, ...props }: ComponentPropsWithoutRef<'div'>): React.JSX.Element {
  return <div className={cn('p-5', className)} {...props} />;
}

function CardFooter({ className, ...props }: ComponentPropsWithoutRef<'footer'>): React.JSX.Element {
  return <footer className={cn('border-t border-slate-100 p-5', className)} {...props} />;
}

export { Card, CardContent, CardFooter, CardHeader, CardTitle };