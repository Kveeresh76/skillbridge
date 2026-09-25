import { useCallback, useEffect, useState } from 'react';
import WorkspaceShell from '../components/WorkspaceShell';
import api from '../services/api';

export default function Messages() {
  const [threads, setThreads] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [body, setBody] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const { data } = await api.get('/workspace/messages');
    setThreads(data.threads);
    setActiveId((current) => current ?? data.threads[0]?.request_id ?? null);
    return data.threads;
  }, []);

  useEffect(() => { load().catch(() => setError('Your conversations could not be loaded.')); }, [load]);

  const active = threads.find((thread) => thread.request_id === activeId) || null;

  useEffect(() => {
    if (!active || !active.unread) return;
    api.post(`/workspace/messages/${active.request_id}/read`).then(load).catch(() => {});
  }, [active, load]);

  function openThread(requestId) {
    setActiveId(requestId);
    setError('');
  }

  async function send(event) {
    event.preventDefault();
    if (!body.trim() || !active) return;
    try {
      await api.post(`/workspace/messages/${active.request_id}`, { body });
      setBody('');
      await load();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Your message could not be sent.');
    }
  }

  return (
    <WorkspaceShell title="Messages" eyebrow="Stay in the loop">
      <div className="mt-8 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="card p-4">
          <h2 className="px-2 font-display text-xl text-ink-900 dark:text-white">Conversations</h2>
          <ul className="mt-3 space-y-1">
            {threads.map((thread) => (
              <li key={thread.request_id}>
                <button
                  type="button"
                  onClick={() => openThread(thread.request_id)}
                  className={`w-full rounded-md px-3 py-3 text-left text-sm transition-colors ${thread.request_id === activeId ? 'bg-ember-50 text-ink-900 dark:bg-ink-800 dark:text-white' : 'text-ink-600 hover:bg-ink-50 dark:text-ink-300 dark:hover:bg-ink-800'}`}
                >
                  <span className="flex items-center justify-between gap-2">
                    <span className="font-medium">{thread.partner}</span>
                    {thread.unread > 0 && <span className="rounded-full bg-ember-500 px-2 py-0.5 text-xs text-white">{thread.unread}</span>}
                  </span>
                  <span className="mt-1 block text-xs text-ink-400">{thread.teaching_skill} ↔ {thread.learning_skill}</span>
                </button>
              </li>
            ))}
          </ul>
          {!threads.length && <p className="px-2 py-4 text-sm text-ink-500">Your conversations will appear here after an exchange request is accepted.</p>}
        </div>

        <div className="card flex flex-col p-6">
          <div className="max-h-[26rem] flex-1 space-y-4 overflow-y-auto">
            {active?.messages.length ? active.messages.map((message) => (
              <div className={`max-w-[85%] rounded-lg px-4 py-3 ${message.is_mine ? 'ml-auto bg-ember-50 dark:bg-ink-800' : 'bg-ink-50 dark:bg-ink-900'}`} key={message.id}>
                <p className="text-xs text-ink-400">{message.sender} · {new Date(message.created_at).toLocaleString()}</p>
                <p className="mt-1 text-sm text-ink-700 dark:text-ink-200">{message.body}</p>
              </div>
            )) : <p className="text-sm text-ink-500">{active ? 'Say hello to get this exchange moving.' : 'Select a conversation to start reading.'}</p>}
          </div>
          {error && <p className="mt-4 text-sm text-red-700" role="alert">{error}</p>}
          <form className="mt-6 flex gap-2" onSubmit={send}>
            <input
              className="input-field"
              placeholder={active ? `Message ${active.partner}` : 'No active conversation'}
              value={body}
              onChange={(event) => setBody(event.target.value)}
              disabled={!active}
            />
            <button className="btn-primary" disabled={!body.trim() || !active}>Send</button>
          </form>
        </div>
      </div>
    </WorkspaceShell>
  );
}
