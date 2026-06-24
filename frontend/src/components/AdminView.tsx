import { useState, useEffect } from 'react';
import type { Toast as ToastType } from '@/hooks/useToast';

interface User {
  id: number;
  username: string;
  is_admin: boolean;
}

interface AdminViewProps {
  token: string;
  toasts: ToastType[];
  onRemoveToast: (id: string) => void;
  onToast: (message: string, type: 'success' | 'error') => void;
}

export default function AdminView({ token, onToast }: AdminViewProps) {
  const [allowSignups, setAllowSignups] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [loaded, setLoaded] = useState(false);

  const loadAdminData = async () => {
    try {
      const [settingsRes, usersRes] = await Promise.all([
        fetch('/admin/settings'),
        fetch('/admin/users', { headers: { Authorization: `Bearer ${token}` } }),
      ]);

      if (settingsRes.ok) {
        const settings = await settingsRes.json();
        setAllowSignups(settings.allow_signups);
      }
      if (usersRes.ok) {
        const userList = await usersRes.json();
        setUsers(userList);
      }
      setLoaded(true);
    } catch {
      onToast('Failed to load admin data', 'error');
    }
  };

  useEffect(() => {
    loadAdminData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const toggleSignups = async () => {
    try {
      await fetch('/admin/toggle-signups', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      loadAdminData();
      onToast(`Signups ${allowSignups ? 'closed' : 'opened'}`, 'success');
    } catch {
      onToast('Failed to toggle signups', 'error');
    }
  };

  if (!loaded) {
    return (
      <div className="flex items-center justify-center py-12 animate-fade-in-up">
        <div className="w-6 h-6 border-2 border-vault-accent/30 border-t-vault-accent rounded-full animate-spin-loader" />
      </div>
    );
  }

  return (
    <div className="animate-fade-in-up space-y-6">
      {/* Registration Toggle */}
      <div className="bg-obsidian-elevated rounded-md border border-obsidian-border-subtle p-4 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-obsidian-text-primary">Open Registration</p>
          <p className="text-xs text-obsidian-text-secondary mt-0.5">
            Allow new users to create accounts
          </p>
        </div>
        <button
          onClick={toggleSignups}
          className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all cursor-pointer ${
            allowSignups
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20'
              : 'bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20'
          }`}
        >
          {allowSignups ? 'OPEN' : 'CLOSED'}
        </button>
      </div>

      {/* User List */}
      <div>
        <h3 className="text-sm font-semibold text-obsidian-text-primary mb-3">
          Registered Users
        </h3>
        <div className="max-h-[220px] overflow-y-auto vault-scrollbar space-y-2 pr-1">
          {users.map(user => (
            <div
              key={user.id}
              className="flex items-center justify-between bg-obsidian-elevated rounded-md border border-obsidian-border-subtle px-4 py-3"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-obsidian-text-primary">
                  {user.username}
                </span>
                {user.is_admin && (
                  <span className="text-[10px] uppercase tracking-wider bg-vault-admin-badge/10 text-vault-admin-badge px-2 py-0.5 rounded-sm border border-vault-admin-badge/20">
                    Admin
                  </span>
                )}
              </div>
              <span className="text-xs text-obsidian-text-muted font-mono">
                ID: {user.id}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
