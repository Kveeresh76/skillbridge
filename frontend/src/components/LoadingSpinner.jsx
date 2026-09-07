export default function LoadingSpinner({ label = 'Loading' }) {
  return (
    <div className="flex items-center justify-center gap-2 py-10 text-ink-400" role="status" aria-live="polite">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-ink-200 border-t-ink-600 dark:border-ink-700 dark:border-t-ember-400" />
      <span className="text-sm">{label}</span>
    </div>
  );
}
