import { useState, useEffect } from 'react';
import AuthCard from './components/AuthCard';
import Dashboard from './components/Dashboard';

export default function App() {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string>('');
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('vault_token');
    if (stored) {
      setToken(stored);
      setUsername('User');
    }
    setIsReady(true);
  }, []);

  const handleLogin = (newToken: string, newUsername: string) => {
    setToken(newToken);
    setUsername(newUsername);
    localStorage.setItem('vault_token', newToken);
  };

  const handleLogout = () => {
    setToken(null);
    setUsername('');
    localStorage.removeItem('vault_token');
  };

  if (!isReady) {
    return (
      <div className="min-h-screen bg-obsidian-base flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-vault-accent/30 border-t-vault-accent rounded-full animate-spin-loader" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-obsidian-base flex items-center justify-center p-4 relative overflow-hidden">
      {/* Ambient background glow */}
      <div
        className="absolute pointer-events-none"
        style={{
          width: '600px',
          height: '500px',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'radial-gradient(ellipse 600px 500px at 50% 50%, rgba(108, 92, 231, 0.06), transparent)',
        }}
      />

      {token ? (
        <Dashboard username={username} token={token} onLogout={handleLogout} />
      ) : (
        <AuthCard onLogin={handleLogin} />
      )}
    </div>
  );
}
