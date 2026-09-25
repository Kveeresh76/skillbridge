import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import Messages from './Messages';
import { AuthProvider } from '../context/AuthContext';
import api from '../services/api';

vi.mock('../services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), put: vi.fn() },
}));

const threads = [
  {
    request_id: 7,
    partner: 'Ada Lovelace',
    teaching_skill: 'Python',
    learning_skill: 'UI/UX Design',
    unread: 1,
    last_activity: '2026-01-02T10:00:00Z',
    messages: [{ id: 1, body: 'When shall we start?', sender: 'Ada Lovelace', is_mine: false, is_read: false, created_at: '2026-01-02T10:00:00Z' }],
  },
  {
    request_id: 9,
    partner: 'Grace Hopper',
    teaching_skill: 'SQL',
    learning_skill: 'Guitar',
    unread: 0,
    last_activity: '2026-01-01T10:00:00Z',
    messages: [{ id: 2, body: 'Thanks for the session!', sender: 'You', is_mine: true, is_read: true, created_at: '2026-01-01T10:00:00Z' }],
  },
];

function renderMessages() {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <Messages />
      </AuthProvider>
    </BrowserRouter>
  );
}

describe('Messages', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.get.mockResolvedValue({ data: { threads } });
    api.post.mockResolvedValue({ data: {} });
  });

  it('opens the newest thread and marks it as read', async () => {
    renderMessages();
    expect(await screen.findByText('When shall we start?')).toBeInTheDocument();
    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/workspace/messages/7/read'));
  });

  it('sends a reply to the thread the user selected', async () => {
    renderMessages();
    await userEvent.click(await screen.findByRole('button', { name: /Grace Hopper/ }));
    await userEvent.type(screen.getByPlaceholderText('Message Grace Hopper'), 'See you then');
    await userEvent.click(screen.getByRole('button', { name: 'Send' }));

    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/workspace/messages/9', { body: 'See you then' }));
  });
});
