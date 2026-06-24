import { useState, useCallback, useRef, useEffect } from 'react';

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error';
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timersRef = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
    const timer = timersRef.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timersRef.current.delete(id);
    }
  }, []);

  const addToast = useCallback((message: string, type: 'success' | 'error') => {
    const id = `${Date.now()}-${Math.random()}`;
    setToasts(prev => [...prev, { id, message, type }]);

    const timer = setTimeout(() => {
      removeToast(id);
    }, 4000);
    timersRef.current.set(id, timer);
  }, [removeToast]);

  useEffect(() => {
    return () => {
      timersRef.current.forEach(timer => clearTimeout(timer));
    };
  }, []);

  return { toasts, addToast, removeToast };
}
