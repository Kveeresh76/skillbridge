import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function WorkspaceShell({ title, eyebrow, children }) {
  const { user, logout } = useAuth();
  return <div className="min-h-screen bg-surface-light dark:bg-surface-dark"><header className="border-b border-ink-100 bg-white dark:border-ink-800 dark:bg-ink-950"><div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5"><Link to="/dashboard" className="font-display text-xl font-semibold text-ink-900 dark:text-ink-50">SkillBridge</Link><nav className="flex items-center gap-4 text-sm text-ink-500"><Link to="/discover">Discover</Link><Link to="/dashboard">Dashboard</Link><Link to="/profile" className="font-medium text-ink-900 dark:text-white">{user?.username}</Link><button type="button" onClick={logout}>Log out</button></nav></div></header><main className="mx-auto max-w-6xl px-6 py-10"><p className="text-sm font-medium uppercase tracking-[0.16em] text-ember-600">{eyebrow || 'SkillBridge'}</p><h1 className="mt-3 font-display text-4xl text-ink-900 dark:text-ink-50">{title}</h1>{children}</main></div>;
}
