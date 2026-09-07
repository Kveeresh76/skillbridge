import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, BookOpen, CalendarDays, Coins, MessageCircle, Search, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const activity = [
  { icon: MessageCircle, title: 'Your exchange inbox is ready', detail: 'Keep conversations moving with your learning partners.', href: '/messages' },
  { icon: BookOpen, title: 'Complete your skill profile', detail: 'Add skills you offer and want to learn to improve matches.', href: '/profile' },
  { icon: CalendarDays, title: 'Plan your next session', detail: 'Your calendar is the place for focused learning time.', href: '/sessions' },
];

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [summaryError, setSummaryError] = useState('');
  const firstName = user?.full_name?.split(' ')[0] || user?.username || 'there';

  useEffect(() => {
    let isMounted = true;
    api.get('/dashboard/summary')
      .then(({ data }) => {
        if (isMounted) setSummary(data);
      })
      .catch(() => {
        if (isMounted) setSummaryError('Dashboard details could not be loaded. Please refresh the page.');
      });
    return () => { isMounted = false; };
  }, []);

  const nextSession = summary?.next_session;
  const sessionDate = nextSession ? new Date(nextSession.start_time).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) : null;

  return (
    <div className="min-h-screen bg-surface-light dark:bg-surface-dark">
      <header className="border-b border-ink-100 bg-white dark:border-ink-800 dark:bg-ink-950">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <Link to="/" className="font-display text-xl font-semibold text-ink-900 dark:text-ink-50">SkillBridge</Link>
          <nav className="flex items-center gap-4 text-sm text-ink-500 dark:text-ink-300">
            <Link className="hidden hover:text-ink-900 dark:hover:text-white sm:block" to="/discover">Discover</Link>
            <Link className="hidden hover:text-ink-900 dark:hover:text-white sm:block" to="/messages">Messages</Link>
            <Link className="flex h-9 w-9 items-center justify-center rounded-full bg-ember-100 font-medium text-ember-800" to="/profile" aria-label="Open profile">
              {firstName.charAt(0).toUpperCase()}
            </Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10 sm:py-14">
        <section className="flex flex-col justify-between gap-6 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.16em] text-ember-600">Your exchange desk</p>
            <h1 className="mt-3 font-display text-4xl text-ink-900 dark:text-ink-50 sm:text-5xl">Good morning, {firstName}.</h1>
            <p className="mt-3 max-w-xl text-ink-500 dark:text-ink-300">Teach a little. Learn a lot. Your next useful exchange is a few clicks away.</p>
          </div>
          <Link to="/discover" className="btn-primary shrink-0"><Search className="h-4 w-4" /> Find a skill</Link>
        </section>

        <section className="mt-10 grid gap-4 sm:grid-cols-3">
          <div className="card border-l-4 border-l-ember-500 p-5">
            <Coins className="h-5 w-5 text-ember-500" />
            <p className="mt-5 text-sm text-ink-500 dark:text-ink-300">Skill Credits</p>
            <p className="mt-1 font-display text-3xl text-ink-900 dark:text-ink-50">{summary?.skill_credits ?? user?.skill_credits ?? 0}</p>
          </div>
          <div className="card p-5">
            <CalendarDays className="h-5 w-5 text-ink-500" />
            <p className="mt-5 text-sm text-ink-500 dark:text-ink-300">Upcoming sessions</p>
            <p className="mt-1 font-display text-3xl text-ink-900 dark:text-ink-50">{summary?.upcoming_sessions ?? '...'}</p>
          </div>
          <div className="card p-5">
            <MessageCircle className="h-5 w-5 text-ink-500" />
            <p className="mt-5 text-sm text-ink-500 dark:text-ink-300">Unread messages</p>
            <p className="mt-1 font-display text-3xl text-ink-900 dark:text-ink-50">{summary?.unread_messages ?? '...'}</p>
          </div>
        </section>

        <section className="mt-10 grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <div className="card p-6 sm:p-8">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.14em] text-ink-400">Next up</p>
                <h2 className="mt-2 font-display text-2xl text-ink-900 dark:text-ink-50">{nextSession ? `Learn ${nextSession.skill}` : 'Make your first exchange'}</h2>
              </div>
              <Sparkles className="h-6 w-6 shrink-0 text-ember-500" />
            </div>
            <p className="mt-4 max-w-lg text-sm leading-6 text-ink-500 dark:text-ink-300">
              {nextSession ? `${sessionDate} with ${nextSession.partner_name}.` : 'Browse people who can teach what you want to learn, then start a conversation around a skill you can share in return.'}
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              {nextSession ? <a href={nextSession.meeting_link} className="btn-primary" target="_blank" rel="noreferrer">Open session <ArrowUpRight className="h-4 w-4" /></a> : <Link to="/discover" className="btn-primary">Explore matches <ArrowUpRight className="h-4 w-4" /></Link>}
              <Link to={nextSession ? '/sessions' : '/profile'} className="btn-secondary">{nextSession ? 'View sessions' : 'Edit my skills'}</Link>
            </div>
          </div>

          <div>
            <h2 className="font-display text-2xl text-ink-900 dark:text-ink-50">Keep building</h2>
            <div className="mt-4 space-y-3">
              {activity.map(({ icon: Icon, title, detail, href }) => (
                <Link key={title} to={href} className="card flex gap-4 p-4 transition-transform hover:-translate-y-0.5">
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-ink-100 text-ink-600 dark:bg-ink-800 dark:text-ember-300"><Icon className="h-4 w-4" /></span>
                  <span><span className="block text-sm font-medium text-ink-900 dark:text-ink-50">{title}</span><span className="mt-1 block text-xs leading-5 text-ink-500 dark:text-ink-300">{detail}</span></span>
                </Link>
              ))}
            </div>
          </div>
        </section>
        {summaryError && <p className="mt-6 text-sm text-red-700" role="alert">{summaryError}</p>}
      </main>
    </div>
  );
}
