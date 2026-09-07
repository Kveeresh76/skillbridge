import { Link } from 'react-router-dom';
import { ArrowUpRight, BookOpen, Coins, MessageCircle } from 'lucide-react';

const steps = [
  {
    title: 'Share your skill',
    body: 'Tell the community what you can teach — from Python to public speaking.',
  },
  {
    title: 'Earn Skill Credits',
    body: 'Run a session for someone and a credit lands in your balance.',
  },
  {
    title: 'Learn something new',
    body: 'Spend that credit on a session with someone who can teach you.',
  },
];

const features = [
  { icon: BookOpen, title: 'Smart matching', body: 'We pair what you offer against what someone else wants, and score the fit.' },
  { icon: MessageCircle, title: 'Real-time chat', body: 'Work out the details and keep talking once a request is accepted.' },
  { icon: Coins, title: 'Skill Credits', body: 'A simple ledger: teach to earn, learn to spend. No cash changes hands.' },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-surface-light dark:bg-surface-dark">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <span className="font-display text-xl font-semibold text-ink-900 dark:text-ink-50">SkillBridge</span>
        <nav className="flex items-center gap-3">
          <Link to="/login" className="btn-secondary">Log in</Link>
          <Link to="/register" className="btn-primary">Start learning</Link>
        </nav>
      </header>

      <section className="mx-auto grid max-w-6xl gap-10 px-6 pb-24 pt-12 md:grid-cols-2 md:items-center md:pt-20">
        <div>
          <h1 className="font-display text-5xl leading-[1.05] text-ink-900 dark:text-ink-50 md:text-6xl">
            Knowledge is the new currency.
          </h1>
          <p className="mt-6 max-w-md text-lg text-ink-600 dark:text-ink-200">
            Teach what you know. Learn what you love. Exchange skills with people around you — no tuition, just trade.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/register" className="btn-primary">
              Start learning <ArrowUpRight className="h-4 w-4" />
            </Link>
            <Link to="/discover" className="btn-secondary">Explore skills</Link>
          </div>
        </div>
        <div className="card p-8">
          <p className="text-sm text-ink-400">How the exchange works</p>
          <ol className="mt-4 space-y-5">
            {steps.map((step, i) => (
              <li key={step.title} className="flex gap-4">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ink-900 font-mono text-sm text-white dark:bg-ember-500">
                  {i + 1}
                </span>
                <div>
                  <p className="font-medium text-ink-900 dark:text-ink-50">{step.title}</p>
                  <p className="text-sm text-ink-500 dark:text-ink-300">{step.body}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="border-t border-ink-100 bg-white py-20 dark:border-ink-800 dark:bg-ink-950">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="font-display text-3xl text-ink-900 dark:text-ink-50">Built for the exchange, not the transaction</h2>
          <div className="mt-10 grid gap-8 md:grid-cols-3">
            {features.map(({ icon: Icon, title, body }) => (
              <div key={title}>
                <Icon className="h-6 w-6 text-ember-500" />
                <h3 className="mt-4 text-lg font-medium text-ink-900 dark:text-ink-50">{title}</h3>
                <p className="mt-2 text-sm text-ink-500 dark:text-ink-300">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
