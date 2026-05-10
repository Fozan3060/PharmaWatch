import { useState } from 'react';

import AgentTracePanel from '../components/AgentTracePanel.jsx';
import InvestigationProgress from '../components/InvestigationProgress.jsx';
import InvestigationReport from '../components/InvestigationReport.jsx';
import StructuredReportForm from '../components/StructuredReportForm.jsx';
import useAgentStream from '../hooks/useAgentStream.js';

export default function InvestigatePage() {
  const { events, status, errorMessage, investigate, reset } = useAgentStream();
  const [traceOpen, setTraceOpen] = useState(false);
  const showProgress = status === 'streaming' || status === 'done';
  const showReport = events.some((e) => e.event === 'tool_result' || e.event === 'final');

  return (
    <div className="space-y-6">
      <section className="space-y-1">
        <h1 className="text-3xl">Investigate a complaint</h1>
        <p className="max-w-3xl text-sm text-slate-600">
          Pick the medicine, enter the price you were charged, and identify the pharmacy.
          The agent verifies the price against DRAP, checks for counterfeit/substandard
          alerts, surfaces the pharmacy&rsquo;s prior enforcement history, and prepares
          your complaint — you watch every step live.
        </p>
      </section>

      <StructuredReportForm onSubmit={investigate} disabled={status === 'streaming'} />

      {status === 'error' && <AgentErrorCard message={errorMessage} onRetry={reset} />}

      {showProgress && <InvestigationProgress events={events} status={status} />}

      {showReport && <InvestigationReport events={events} />}

      {events.length > 0 && (
        <div className="card">
          <button
            type="button"
            onClick={() => setTraceOpen((o) => !o)}
            className="flex w-full items-center justify-between text-sm font-medium text-slate-700"
          >
            <span>Agent trace ({events.length} events)</span>
            <span className="text-xs text-slate-400">{traceOpen ? 'hide ▲' : 'show ▼'}</span>
          </button>
          {traceOpen && (
            <div className="mt-3">
              <AgentTracePanel events={events} status={status} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function AgentErrorCard({ message, onRetry }) {
  const isRateLimit = /429|RESOURCE_EXHAUSTED|quota/i.test(message || '');
  const isAuth = /401|API key|GEMINI_API_KEY/i.test(message || '');

  if (isRateLimit) {
    return (
      <div className="card border-l-4 border-yellow-500">
        <div className="font-medium text-yellow-700">⏳ Gemini quota exhausted</div>
        <div className="mt-1 text-sm text-slate-700">
          You&rsquo;ve hit the Gemini free-tier daily limit (20 requests/day for{' '}
          <code>gemini-2.5-flash</code>). The agent itself is fine — Google is rate-limiting
          us.
        </div>
        <div className="mt-2 text-xs text-slate-500">
          Options:
          <ul className="ml-4 mt-1 list-disc space-y-0.5">
            <li>Wait for the daily quota to reset (resets at midnight Pacific time)</li>
            <li>
              Add billing in{' '}
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className="text-brand-500 underline"
              >
                Google AI Studio
              </a>{' '}
              to upgrade to paid tier (no further limits during demos)
            </li>
            <li>
              Switch the model in <code>backend/.env</code> to{' '}
              <code>gemini-2.5-flash-lite</code> (different quota pool)
            </li>
          </ul>
        </div>
        <button onClick={onRetry} className="btn-secondary mt-3 text-xs">
          Retry
        </button>
      </div>
    );
  }

  if (isAuth) {
    return (
      <div className="card border-l-4 border-red-500">
        <div className="font-medium text-red-700">🔑 API key issue</div>
        <div className="mt-1 text-sm text-slate-700">
          Gemini rejected the API key. Make sure <code>GEMINI_API_KEY</code> in{' '}
          <code>backend/.env</code> is valid (get one at{' '}
          <a
            href="https://aistudio.google.com/app/apikey"
            target="_blank"
            rel="noreferrer"
            className="text-brand-500 underline"
          >
            aistudio.google.com/app/apikey
          </a>
          ).
        </div>
        <button onClick={onRetry} className="btn-secondary mt-3 text-xs">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="card border-l-4 border-red-500">
      <div className="font-medium text-red-700">Agent failed</div>
      <div className="mt-1 break-all text-xs text-slate-700">{message || 'Unknown error.'}</div>
      <button onClick={onRetry} className="btn-secondary mt-3 text-xs">
        Try again
      </button>
    </div>
  );
}
