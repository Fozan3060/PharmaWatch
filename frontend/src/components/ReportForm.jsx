import { useState } from 'react';

const PLACEHOLDER =
  'I was charged Rs. 1,200 for Ceftum 500mg at City Pharmacy, Saddar, Karachi.';

export default function ReportForm({ onSubmit, disabled }) {
  const [text, setText] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSubmit(text.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-3">
      <label htmlFor="report" className="block">
        <span className="block text-sm font-medium text-slate-800">
          Tell us what happened
        </span>
        <span className="mt-1 block text-xs text-slate-500">
          Include the medicine, the price you were charged, and the pharmacy. The agent will
          do the rest — verify against DRAP, find cheaper alternatives, surface prior
          violations, and prepare your complaint.
        </span>
      </label>
      <textarea
        id="report"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={3}
        placeholder={PLACEHOLDER}
        disabled={disabled}
        className="block w-full resize-none rounded-md border border-slate-300 p-3 text-sm shadow-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:bg-slate-100"
      />
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => setText(PLACEHOLDER)}
          disabled={disabled}
          className="text-xs text-brand-500 hover:underline disabled:no-underline"
        >
          Use the demo example
        </button>
        <button type="submit" disabled={disabled || !text.trim()} className="btn-primary">
          {disabled ? 'Investigating…' : 'Investigate'}
        </button>
      </div>
    </form>
  );
}
