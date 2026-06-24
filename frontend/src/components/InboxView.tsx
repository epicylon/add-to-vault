import { useState, type FormEvent } from 'react';
import { BookOpen, Brain, GitMerge } from 'lucide-react';
import { ToastContainer } from './Toast';
import type { Toast as ToastType } from '@/hooks/useToast';

const MODES = [
  {
    id: 'archivist',
    label: 'Archivist',
    description: 'Summarize',
    icon: BookOpen,
  },
  {
    id: 'analyst',
    label: 'Analyst',
    description: 'Deep analysis',
    icon: Brain,
  },
  {
    id: 'synthesist',
    label: 'Synthesist',
    description: 'Connect ideas',
    icon: GitMerge,
  },
] as const;

type ModeId = typeof MODES[number]['id'];

interface InboxViewProps {
  token: string;
  toasts: ToastType[];
  onRemoveToast: (id: string) => void;
  onToast: (message: string, type: 'success' | 'error') => void;
}

export default function InboxView({ token, toasts, onRemoveToast, onToast }: InboxViewProps) {
  const [url, setUrl] = useState('');
  const [mode, setMode] = useState<ModeId>('analyst');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setIsLoading(true);
    try {
      const res = await fetch('/process-link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ url, mode }),
      });

      if (!res.ok) throw new Error('Processing failed');
      const data = await res.json();
      onToast(`Success! Saved to: ${data.path || 'vault'}`, 'success');
      setUrl('');
    } catch (err: unknown) {
      onToast(err instanceof Error ? err.message : 'Processing failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="animate-fade-in-up">
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* URL Input */}
        <div>
          <input
            type="url"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="Paste a URL to process..."
            className="vault-input py-3.5"
            required
          />
        </div>

        {/* Processing Mode */}
        <div>
          <label className="block text-xs font-semibold text-obsidian-text-secondary uppercase tracking-[0.08em] mb-3">
            Processing Mode
          </label>
          <div className="grid grid-cols-3 gap-2">
            {MODES.map(({ id, label, description, icon: Icon }) => {
              const isActive = mode === id;
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => setMode(id)}
                  className={`flex flex-col items-center py-4 px-2 sm:px-3 rounded-md border-[1.5px] transition-all duration-200 cursor-pointer ${
                    isActive
                      ? 'border-vault-accent bg-[rgba(108,92,231,0.12)] shadow-[0_0_20px_rgba(108,92,231,0.15)]'
                      : 'border-obsidian-border-subtle bg-obsidian-elevated hover:border-obsidian-border-medium hover:bg-obsidian-overlay'
                  }`}
                >
                  <Icon
                    size={22}
                    className={`mb-2 transition-colors ${
                      isActive ? 'text-vault-accent' : 'text-obsidian-text-secondary'
                    }`}
                  />
                  <span
                    className={`text-sm font-medium mb-0.5 transition-colors ${
                      isActive ? 'text-vault-accent' : 'text-obsidian-text-secondary'
                    }`}
                  >
                    {label}
                  </span>
                  <span
                    className={`text-xs transition-colors hidden sm:block ${
                      isActive ? 'text-vault-accent/70' : 'text-obsidian-text-muted'
                    }`}
                  >
                    {description}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
          className="vault-btn-primary py-4 text-[0.9375rem] tracking-[0.01em] flex items-center justify-center gap-2 disabled:opacity-70"
        >
          {isLoading ? (
            <div className="w-[18px] h-[18px] border-2 border-white/30 border-t-white rounded-full animate-spin-loader" />
          ) : (
            'Process & Save'
          )}
        </button>
      </form>

      <ToastContainer toasts={toasts} onRemove={onRemoveToast} />
    </div>
  );
}
