import { useEffect, useState } from 'react';
import WorkspaceShell from '../components/WorkspaceShell';
import api from '../services/api';

export default function Requests() {
  const [data, setData] = useState({ incoming: [], outgoing: [] });
  const load = () => api.get('/workspace/requests').then(({ data: value }) => setData(value));
  useEffect(load, []);
  async function update(id, status) { await api.patch(`/workspace/requests/${id}?status=${status}`); load(); }
  const card = (item, incoming) => <div className="card p-5" key={item.id}><div className="flex items-start justify-between gap-3"><div><h2 className="font-medium text-ink-900 dark:text-white">{incoming ? item.sender : item.receiver}</h2><p className="mt-1 text-sm text-ink-500">{item.teaching_skill} ↔ {item.learning_skill}</p></div><span className="text-xs uppercase text-ember-600">{item.status}</span></div><p className="mt-4 text-sm text-ink-500">{item.message}</p>{incoming && item.status === 'PENDING' && <div className="mt-4 flex gap-2"><button className="btn-primary" onClick={() => update(item.id, 'ACCEPTED')}>Accept</button><button className="btn-secondary" onClick={() => update(item.id, 'REJECTED')}>Decline</button></div>}</div>;
  return <WorkspaceShell title="Exchange requests" eyebrow="Your connections"><div className="mt-8 grid gap-8 lg:grid-cols-2"><section><h2 className="font-display text-2xl text-ink-900 dark:text-white">Incoming</h2><div className="mt-4 space-y-3">{data.incoming.length ? data.incoming.map((item) => card(item, true)) : <p className="text-sm text-ink-500">No incoming requests.</p>}</div></section><section><h2 className="font-display text-2xl text-ink-900 dark:text-white">Sent</h2><div className="mt-4 space-y-3">{data.outgoing.length ? data.outgoing.map((item) => card(item, false)) : <p className="text-sm text-ink-500">No sent requests.</p>}</div></section></div></WorkspaceShell>;
}
