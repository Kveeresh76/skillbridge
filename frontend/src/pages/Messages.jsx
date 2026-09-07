import { useEffect, useState } from 'react';
import WorkspaceShell from '../components/WorkspaceShell';
import api from '../services/api';

export default function Messages() {
  const [messages, setMessages] = useState([]); const [body, setBody] = useState('');
  const load = () => api.get('/workspace/messages').then(({ data }) => setMessages(data.messages));
  useEffect(load, []);
  async function send(event) { event.preventDefault(); if (!body.trim() || !messages[0]?.request_id) return; await api.post(`/workspace/messages/${messages[0].request_id}`, { body }); setBody(''); load(); }
  return <WorkspaceShell title="Messages" eyebrow="Stay in the loop"><div className="card mx-auto mt-8 max-w-3xl p-6"><div className="max-h-[28rem] space-y-4 overflow-y-auto">{messages.length ? messages.map((message) => <div className="border-b border-ink-100 pb-4 dark:border-ink-800" key={message.id}><p className="text-xs text-ink-400">{message.sender} · {new Date(message.created_at).toLocaleString()}</p><p className="mt-1 text-sm text-ink-700 dark:text-ink-200">{message.body}</p></div>) : <p className="text-sm text-ink-500">Your conversations will appear here after an exchange request is accepted.</p>}</div><form className="mt-6 flex gap-2" onSubmit={send}><input className="input-field" placeholder={messages.length ? 'Write a message' : 'No active conversation'} value={body} onChange={(e) => setBody(e.target.value)} disabled={!messages.length} /><button className="btn-primary" disabled={!body.trim() || !messages.length}>Send</button></form></div></WorkspaceShell>;
}
