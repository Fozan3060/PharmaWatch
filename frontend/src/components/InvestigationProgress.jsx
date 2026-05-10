// Visible-from-the-first-second status panel that shows the agent's
// investigation steps as they fire. Replaces the silent "ReportSkeleton"
// from before so users can SEE the agent working.

const STEPS = [
  { tool: 'drap_price_lookup', label: 'Verifying price against DRAP' },
  { tool: 'spurious_alert_check', label: 'Checking counterfeit / substandard alerts' },
  { tool: 'generic_alternatives', label: 'Finding cheaper generic alternatives' },
  { tool: 'drap_enforcement_lookup', label: "Checking pharmacy's enforcement history" },
  { tool: 'get_pharmacy_reports', label: 'Reading community fraud signal' },
  { tool: 'generate_complaint_letter', label: 'Drafting formal complaint letter' },
];

function stepStatus(events, tool) {
  if (events.some((e) => e.event === 'tool_error' && e.data?.name === tool)) return 'error';
  if (events.some((e) => e.event === 'tool_result' && e.data?.name === tool)) return 'done';
  if (events.some((e) => e.event === 'tool_call' && e.data?.name === tool)) return 'running';
  return 'pending';
}

const ICON = {
  pending: <span className="text-slate-400">○</span>,
  running: (
    <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
  ),
  done: <span className="text-green-600">✓</span>,
  error: <span className="text-red-500">✗</span>,
};

const ROW_CLASS = {
  pending: 'text-slate-400',
  running: 'text-brand-600 font-medium',
  done: 'text-slate-700',
  error: 'text-red-600',
};

export default function InvestigationProgress({ events, status }) {
  const isStreaming = status === 'streaming';
  const isDone = status === 'done';
  const anyToolFired = events.some((e) => e.event === 'tool_call');
  const finalText = events.find((e) => e.event === 'final')?.data?.text || '';

  // Edge case: agent finished without calling any tool.
  // Two sub-cases: (a) it returned a substantive text reply (e.g. "your price
  // is within MRP, no investigation needed") — surface that text as the
  // answer; (b) it returned nothing useful — show the "needs more info" hint.
  if (isDone && !anyToolFired) {
    if (finalText && finalText.length > 30) {
      return (
        <div className="card border-l-4 border-blue-400">
          <div className="mb-2 flex items-center gap-3">
            <span className="text-blue-500">ℹ</span>
            <h3 className="text-base">Agent response</h3>
          </div>
          <div className="whitespace-pre-wrap text-sm text-slate-700">{finalText}</div>
        </div>
      );
    }
    return (
      <div className="card border-l-4 border-yellow-400">
        <div className="mb-2 flex items-center gap-3">
          <span className="text-yellow-500">⚠</span>
          <h3 className="text-base">The agent needs more info</h3>
        </div>
        <p className="text-sm text-slate-700">
          Try rephrasing with the medicine name, the price you were charged, and the
          pharmacy (with city). For example:{' '}
          <em>&ldquo;I was charged Rs. 1,200 for Ceftum 500mg at City Pharmacy, Saddar,
          Karachi.&rdquo;</em>
        </p>
      </div>
    );
  }

  return (
    <div className="card border-l-4 border-brand-500">
      <div className="mb-3 flex items-center gap-3">
        {isStreaming ? (
          <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
        ) : (
          <span className="text-brand-500">✓</span>
        )}
        <h3 className="text-base">
          {isStreaming ? 'Agent is investigating your complaint…' : 'Investigation complete'}
        </h3>
      </div>
      <ol className="space-y-1.5 text-sm">
        {STEPS.map((step) => {
          const s = stepStatus(events, step.tool);
          return (
            <li key={step.tool} className={`flex items-center gap-3 ${ROW_CLASS[s]}`}>
              <span className="flex h-5 w-5 items-center justify-center">{ICON[s]}</span>
              <span>{step.label}</span>
            </li>
          );
        })}
      </ol>
      {isStreaming && (
        <p className="mt-3 text-xs text-slate-500">
          Each step is a real tool call to local DRAP data, Firestore, or your search backend
          — never a hallucination.
        </p>
      )}
    </div>
  );
}
