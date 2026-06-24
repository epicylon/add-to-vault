import { CheckCircle, AlertCircle, X } from 'lucide-react';
import type { Toast as ToastType } from '@/hooks/useToast';

interface ToastProps {
  toast: ToastType;
  onRemove: (id: string) => void;
}

export default function ToastItem({ toast, onRemove }: ToastProps) {
  const isSuccess = toast.type === 'success';

  return (
    <div
      className={`mt-3 flex items-center gap-2.5 rounded-md px-4 py-3 text-sm animate-toast-in border ${
        isSuccess
          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/15'
          : 'bg-red-500/10 text-red-400 border-red-500/15'
      }`}
    >
      {isSuccess ? (
        <CheckCircle size={16} className="shrink-0" />
      ) : (
        <AlertCircle size={16} className="shrink-0" />
      )}
      <span className="flex-1">{toast.message}</span>
      <button
        onClick={() => onRemove(toast.id)}
        className="shrink-0 opacity-60 hover:opacity-100 transition-opacity cursor-pointer"
      >
        <X size={14} />
      </button>
    </div>
  );
}

interface ToastContainerProps {
  toasts: ToastType[];
  onRemove: (id: string) => void;
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  if (toasts.length === 0) return null;

  return (
    <div className="flex flex-col">
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
}
