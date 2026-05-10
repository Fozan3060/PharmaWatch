import { useMemo, useState } from 'react';

const PLACEHOLDER =
  'I was charged Rs. 1,200 for Ceftum 500mg at City Pharmacy, Saddar, Karachi.';

const MIN_CHARS = 30;

// Cheap heuristic checks — block obvious garbage before round-tripping the
// LLM. Not strict; the agent itself will ask for missing details if a
// minimal-but-vague report sneaks through.
function validate(text) {
  const t = text.trim();
  if (t.length < MIN_CHARS) {
    return `Add a bit more detail — ${MIN_CHARS - t.length} more character${MIN_CHARS - t.length === 1 ? '' : 's'} to go.`;
  }
  if (!/\d/.test(t)) {
    return 'Include the price you were charged (e.g. "Rs. 1,200").';
  }
  if (!/(rs|rupee|pkr)/i.test(t) && !/\d{2,}/.test(t)) {
    return 'Include the price you were charged.';
  }
  // crude word-count check — at least 6 words to have medicine + price + pharmacy
  if (t.split(/\s+/).length < 6) {
    return 'Include the medicine, the price, and the pharmacy.';
  }
  return null;
}

export default function ReportForm({ onSubmit, disabled }) {
  const [text, setText] = useState('');
  const [touched, setTouched] = useState(false);
  const error = useMemo(() => (text.trim() ? validate(text) : null), [text]);
  const showError = touched && error;
  const canSubmit = !disabled && !error && text.trim().length > 0;

  function handleSubmit(e) {
    e.preventDefault();
    setTouched(true);
    if (!canSubmit) return;
    onSubmit(text.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-3">
      <label htmlFor="report" className="block">
        <span className="block text-sm font-medium text-slate-800">
          Tell us what happened
        </span>
        <span className="mt-1 block text-xs text-slate-500">
          Include the <strong>medicine</strong>, the <strong>price you were charged</strong>,
          and the <strong>pharmacy name + city</strong>. The agent will verify the price
          against DRAP, find cheaper alternatives, surface prior violations, and prepare
          your complaint.
        </span>
      </label>
      <textarea
        id="report"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onBlur={() => setTouched(true)}
        rows={3}
        placeholder={PLACEHOLDER}
        disabled={disabled}
        aria-invalid={Boolean(showError)}
        className={`block w-full resize-none rounded-md border p-3 text-sm shadow-sm focus:ring-1 disabled:bg-slate-100 ${
          showError
            ? 'border-red-400 focus:border-red-500 focus:ring-red-500'
            : 'border-slate-300 focus:border-brand-500 focus:ring-brand-500'
        }`}
      />
      {showError && (
        <div className="text-xs text-red-600">⚠ {error}</div>
      )}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => { setText(PLACEHOLDER); setTouched(false); }}
          disabled={disabled}
          className="text-xs text-brand-500 hover:underline disabled:no-underline"
        >
          Use the demo example
        </button>
        <button type="submit" disabled={!canSubmit} className="btn-primary">
          {disabled ? 'Investigating…' : 'Investigate'}
        </button>
      </div>
    </form>
  );
}
