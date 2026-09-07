import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: '', username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });
  async function submit(event) { event.preventDefault(); setError(''); setLoading(true); try { await register(form); navigate('/dashboard', { replace: true }); } catch (request) { setError(request.response?.data?.detail || 'Could not create your account.'); } finally { setLoading(false); } }
  return <main className="min-h-screen bg-surface-light px-6 py-12 dark:bg-surface-dark"><div className="card mx-auto max-w-lg p-8 sm:p-10"><Link to="/" className="font-display text-xl text-ink-900 dark:text-ink-50">SkillBridge</Link><h1 className="mt-10 font-display text-4xl text-ink-900 dark:text-ink-50">Create your account</h1><p className="mt-2 text-sm text-ink-500">Bring one skill to the exchange and leave with another.</p><form className="mt-8 space-y-4" onSubmit={submit}>{[['full_name','Full name','text'],['username','Username','text'],['email','Email','email'],['password','Password','password']].map(([name,label,type]) => <label className="block text-sm font-medium text-ink-800 dark:text-ink-100" key={name}>{label}<input className="input-field mt-2" name={name} type={type} value={form[name]} onChange={update} required minLength={name === 'password' ? 8 : undefined} /></label>)}{error && <p className="text-sm text-red-700" role="alert">{error}</p>}<button className="btn-primary w-full" disabled={loading}>{loading ? 'Creating account...' : 'Create account'}</button></form><p className="mt-6 text-center text-sm text-ink-500">Already a member? <Link className="text-ember-600" to="/login">Sign in</Link></p></div></main>;
}
