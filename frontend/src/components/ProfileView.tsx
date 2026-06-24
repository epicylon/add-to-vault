import { useState, type FormEvent } from 'react';
import { Lock, Eye, EyeOff, Copy, Check, LogOut } from 'lucide-react';
import { ToastContainer } from './Toast';
import type { Toast as ToastType } from '@/hooks/useToast';

interface ProfileViewProps {
  username: string;
  token: string;
  onLogout: () => void;
  toasts: ToastType[];
  onRemoveToast: (id: string) => void;
  onToast: (message: string, type: 'success' | 'error') => void;
}

export default function ProfileView({
  username,
  token,
  onLogout,
  toasts,
  onRemoveToast,
  onToast,
}: ProfileViewProps) {
  const [showToken, setShowToken] = useState(false);
  const [copied, setCopied] = useState(false);
  const [oldPw, setOldPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [isChangingPw, setIsChangingPw] = useState(false);

  const handleCopyToken = async () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(token);
      } else {
        // Fallback
        const textarea = document.createElement('textarea');
        textarea.value = token;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
      }
      setCopied(true);
      onToast('Token copied to clipboard', 'success');
      setTimeout(() => setCopied(false), 1500);
    } catch {
      onToast('Failed to copy token', 'error');
    }
  };

  const handleChangePassword = async (e: FormEvent) => {
    e.preventDefault();
    setIsChangingPw(true);
    try {
      const res = await fetch('/users/me/password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          old_password: oldPw,
          new_password: newPw,
        }),
      });
      if (!res.ok) throw new Error('Failed to change password');
      onToast('Password updated successfully', 'success');
      setOldPw('');
      setNewPw('');
    } catch (err: unknown) {
      onToast(err instanceof Error ? err.message : 'Failed to change password', 'error');
    } finally {
      setIsChangingPw(false);
    }
  };

  return (
    <div className="animate-fade-in-up space-y-4">
      {/* User Info Card */}
      <div className="bg-obsidian-elevated rounded-md border border-obsidian-border-subtle p-4 border-l-[3px] border-l-vault-accent">
        <p className="text-xs text-obsidian-text-secondary mb-1">Logged in as</p>
        <p className="text-lg font-semibold text-obsidian-text-primary">{username}</p>
      </div>

      {/* Token Card */}
      <div className="bg-obsidian-elevated rounded-md border border-obsidian-border-subtle p-4 relative">
        <div className="flex items-center gap-1.5 mb-2">
          <Lock size={12} className="text-obsidian-text-secondary" />
          <p className="text-xs text-obsidian-text-secondary">Bearer Token</p>
          <span className="text-xs text-obsidian-text-muted">for Obsidian plugin</span>
        </div>

        <div className="font-mono text-xs text-obsidian-text-primary p-3 bg-obsidian-base rounded-sm border border-obsidian-border-subtle break-all transition-all duration-250">
          <span className={showToken ? '' : 'blur-[4px] select-none'}>
            {token}
          </span>
        </div>

        {/* Action Row */}
        <div className="flex flex-wrap gap-2 mt-3">
          <button
            onClick={() => setShowToken(!showToken)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-sm bg-obsidian-overlay text-obsidian-text-secondary text-xs font-medium border border-obsidian-border-subtle hover:text-obsidian-text-primary hover:border-obsidian-border-medium transition-all cursor-pointer"
          >
            {showToken ? <EyeOff size={14} /> : <Eye size={14} />}
            {showToken ? 'Hide' : 'Show'}
          </button>

          <button
            onClick={handleCopyToken}
            className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-sm text-xs font-medium border transition-all cursor-pointer ${
              copied
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-[rgba(108,92,231,0.12)] text-vault-accent border-obsidian-border-accent hover:bg-[rgba(108,92,231,0.18)]'
            }`}
          >
            {copied ? (
              <>
                <Check size={14} className="animate-pop-check" />
                Copied!
              </>
            ) : (
              <>
                <Copy size={14} />
                Copy
              </>
            )}
          </button>
        </div>
      </div>

      {/* Password Change */}
      <div className="border-t border-obsidian-border-subtle pt-5 mt-2">
        <h3 className="text-sm font-semibold text-obsidian-text-primary mb-3">
          Change Password
        </h3>
        <form onSubmit={handleChangePassword} className="space-y-3">
          <input
            type="password"
            value={oldPw}
            onChange={e => setOldPw(e.target.value)}
            placeholder="Old password"
            className="vault-input py-2.5 text-sm"
            required
          />
          <input
            type="password"
            value={newPw}
            onChange={e => setNewPw(e.target.value)}
            placeholder="New password"
            className="vault-input py-2.5 text-sm"
            required
          />
          <button
            type="submit"
            disabled={isChangingPw}
            className="vault-btn-secondary w-full py-3 text-sm disabled:opacity-70"
          >
            {isChangingPw ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin-loader mx-auto" />
            ) : (
              'Update password'
            )}
          </button>
        </form>
      </div>

      <ToastContainer toasts={toasts} onRemove={onRemoveToast} />

      {/* Logout */}
      <div className="border-t border-obsidian-border-subtle pt-4">
        <button
          onClick={onLogout}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-md border border-red-500/20 text-red-400 bg-red-500/10 font-medium text-sm hover:bg-red-500/[0.15] hover:border-red-500/30 transition-all active:scale-[0.98] cursor-pointer"
        >
          <LogOut size={16} />
          Log out
        </button>
      </div>
    </div>
  );
}
