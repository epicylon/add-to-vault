import { useState, useEffect } from 'react';
import InboxView from './InboxView';
import ProfileView from './ProfileView';
import AdminView from './AdminView';
import { useToast } from '@/hooks/useToast';

type TabId = 'inbox' | 'profile' | 'admin';

interface DashboardProps {
  username: string;
  token: string;
  onLogout: () => void;
}

export default function Dashboard({ username, token, onLogout }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<TabId>('inbox');
  const [isAdmin, setIsAdmin] = useState(false);
  const { toasts, addToast, removeToast } = useToast();

  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const res = await fetch('/users/me', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const userData = await res.json();
          setIsAdmin(!!userData.is_admin);
        }
      } catch {
        // silently fail
      }
    };
    checkAdmin();
  }, [token]);

  const tabs: { id: TabId; label: string }[] = [
    { id: 'inbox', label: 'Inbox' },
    { id: 'profile', label: 'Profile' },
  ];

  return (
    <div className="w-full max-w-[460px] animate-fade-in-up">
      <div className="vault-card p-5 sm:p-6">
        {/* Tab Navigation */}
        <div className="flex border-b border-obsidian-border-subtle mb-6 -mb-px">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-2.5 px-4 text-sm font-medium transition-all duration-200 cursor-pointer border-b-2 -mb-px ${
                activeTab === tab.id
                  ? 'text-obsidian-text-primary border-b-vault-accent'
                  : 'text-obsidian-text-secondary border-b-transparent hover:text-obsidian-text-primary'
              }`}
            >
              {tab.label}
            </button>
          ))}
          {isAdmin && (
            <button
              onClick={() => setActiveTab('admin')}
              className={`pb-2.5 px-4 text-sm font-medium transition-all duration-200 cursor-pointer border-b-2 -mb-px ${
                activeTab === 'admin'
                  ? 'text-vault-admin-badge border-b-vault-admin-badge'
                  : 'text-vault-admin-badge/70 border-b-transparent hover:text-vault-admin-badge'
              }`}
            >
              Admin
            </button>
          )}
        </div>

        {/* Views */}
        <div className="min-h-[200px]">
          {activeTab === 'inbox' && (
            <InboxView
              token={token}
              toasts={toasts}
              onRemoveToast={removeToast}
              onToast={addToast}
            />
          )}
          {activeTab === 'profile' && (
            <ProfileView
              username={username}
              token={token}
              onLogout={onLogout}
              toasts={toasts}
              onRemoveToast={removeToast}
              onToast={addToast}
            />
          )}
          {activeTab === 'admin' && isAdmin && (
            <AdminView
              token={token}
              toasts={toasts}
              onRemoveToast={removeToast}
              onToast={addToast}
            />
          )}
        </div>
      </div>
    </div>
  );
}
