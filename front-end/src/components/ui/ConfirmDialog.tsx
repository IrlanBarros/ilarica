import { Button } from './Button';

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel: string;
  isLoading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({ open, title, description, confirmLabel, isLoading = false, onConfirm, onCancel }: ConfirmDialogProps): React.JSX.Element | null {
  if (!open) return null;
  return <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 px-4" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget && !isLoading) onCancel(); }}>
    <section role="alertdialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-description" className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
      <h2 id="confirm-title" className="font-display text-xl font-extrabold text-[#7a1e1e]">{title}</h2>
      <p id="confirm-description" className="mt-2 text-sm leading-relaxed text-ilarica-muted">{description}</p>
      <div className="mt-6 flex justify-end gap-3"><Button variant="secondary" disabled={isLoading} onClick={onCancel}>Cancelar</Button><Button variant="danger" isLoading={isLoading} loadingText="Excluindo..." onClick={onConfirm}>{confirmLabel}</Button></div>
    </section>
  </div>;
}
