import { useState } from 'react';

export default function ChatInput({ onSubmit, loading }) {
  const [value, setValue] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || loading) {
      return;
    }
    onSubmit(trimmed);
    setValue('');
  };

  return (
    <form onSubmit={handleSubmit} className="mt-auto flex gap-2">
      <input
        type="text"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Type your experiment, e.g., mix magnesium with hydrochloric acid"
        className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none"
      />
      <button
        type="submit"
        disabled={loading || !value.trim()}
        className="rounded-lg bg-teal-500 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? 'Running…' : 'Run'}
      </button>
    </form>
  );
}
