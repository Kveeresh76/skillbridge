import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import App from './App';
import { AuthProvider } from './context/AuthContext';

describe('App', () => {
  it('renders the SkillBridge landing page at the root route', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    );
    expect(screen.getByText(/Knowledge is the new currency/i)).toBeInTheDocument();
  });
});
