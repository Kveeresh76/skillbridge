import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ArrowRight, KeyRound, Mail } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const destination = location.state?.from?.pathname || '/dashboard';

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      await login(email, password);
      navigate(destination, { replace: true });
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to sign in. Please check your details.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-surface-light px-6 py-12 dark:bg-surface-dark sm:py-20">
      <div className="mx-auto grid max-w-5xl overflow-hidden rounded-xl border border-ink-100 bg-white shadow-raised dark:border-ink-800 dark:bg-ink-900 md:grid-cols-[1.05fr_0.95fr]">
        <section className="bg-ink-900 px-8 py-12 text-white sm:px-12 md:py-16">
          <Link to="/" className="font-display text-2xl">SkillBridge</Link>
          <div className="mt-20 max-w-sm">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-ember-300">Welcome back</p>
            <h1 className="mt-4 font-display text-4xl leading-tight sm:text-5xl">Keep the exchange moving.</h1>
            <p className="mt-5 text-ink-200">Sign in to find your next learning partner, session, or useful conversation.</p>
          </div>
        </section>

        <section className="px-8 py-12 sm:px-12 md:py-16">
          <h2 className="font-display text-3xl text-ink-900 dark:text-ink-50">Sign in</h2>
          <p className="mt-2 text-sm text-ink-500 dark:text-ink-300">Use your SkillBridge account details.</p>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <label className="block text-sm font-medium text-ink-800 dark:text-ink-100">
              Email
              <span className="relative mt-2 block">
                <Mail className="pointer-events-none absolute left-3 top-2.5 h-5 w-5 text-ink-400" aria-hidden="true" />
                <input className="input-field pl-10" type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" required />
              </span>
            </label>
            <label className="block text-sm font-medium text-ink-800 dark:text-ink-100">
              Password
              <span className="relative mt-2 block">
                <KeyRound className="pointer-events-none absolute left-3 top-2.5 h-5 w-5 text-ink-400" aria-hidden="true" />
                <input className="input-field pl-10" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required />
              </span>
            </label>

            {error && <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">{error}</p>}

            <button className="btn-primary w-full" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : 'Sign in'}
              {!isSubmitting && <ArrowRight className="h-4 w-4" aria-hidden="true" />}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-ink-500 dark:text-ink-300">
            New to SkillBridge? <Link className="font-medium text-ember-600 hover:text-ember-700" to="/register">Create an account</Link>
          </p>
        </section>
      </div>
    </main>
  );
}
