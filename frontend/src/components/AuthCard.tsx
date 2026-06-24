import { useState, type FormEvent } from 'react';
import { AlertCircle } from 'lucide-react';

interface AuthCardProps {
  onLogin: (token: string, username: string) => void;
}

type AuthMode = 'login' | 'register';

export default function AuthCard({ onLogin }: AuthCardProps) {
  const [mode, setMode] = useState<AuthMode>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const switchMode = (newMode: AuthMode) => {
    setMode(newMode);
    setError('');
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (mode === 'register') {
        const res = await fetch('/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password, sync_strategy: 'plugin' }),
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || 'Registration error');
        }
      }

      const fd = new FormData();
      fd.append('username', username);
      fd.append('password', password);

      const loginRes = await fetch('/token', {
        method: 'POST',
        body: fd,
      });

      if (!loginRes.ok) throw new Error('Login failed');
      const data = await loginRes.json();
      onLogin(data.access_token, username);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-[420px] animate-fade-in-up">
      <div className="vault-card">
        {/* Title */}
        <h1 className="text-center text-[1.375rem] font-bold text-obsidian-text-primary mb-6 tracking-tight">
          Add To Vault
        </h1>

        {/* Tab Switcher */}
        <div className="flex justify-center">
          <div className="inline-flex bg-obsidian-elevated rounded-full p-[3px] gap-1">
            <button
              onClick={() => switchMode('login')}
              className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-200 cursor-pointer ${
                mode === 'login'
                  ? 'bg-obsidian-overlay text-obsidian-text-primary shadow-[inset_0_1px_2px_rgba(0,0,0,0.2)]'
                  : 'text-obsidian-text-secondary hover:text-obsidian-text-primary'
              }`}
            >
              Log in
            </button>
            <button
              onClick={() => switchMode('register')}
              className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-200 cursor-pointer ${
                mode === 'register'
                  ? 'bg-obsidian-overlay text-obsidian-text-primary shadow-[inset_0_1px_2px_rgba(0,0,0,0.2)]'
                  : 'text-obsidian-text-secondary hover:text-obsidian-text-primary'
              }`}
            >
              Register
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-obsidian-text-secondary mb-1">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              className="vault-input"
              required
              autoComplete="username"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-obsidian-text-secondary mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="vault-input"
              required
              autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="vault-btn-primary mt-1 flex items-center justify-center gap-2 disabled:opacity-70"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin-loader" />
            ) : (
              mode === 'login' ? 'Log in' : 'Register'
            )}
          </button>

          {/* Error */}
          {error && (
            <div className="flex items-center gap-2 bg-red-500/10 text-red-400 text-sm rounded-md px-3.5 py-2.5 border border-red-500/15 animate-toast-in">
              <AlertCircle size={16} className="shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
