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
          Describe what happened in plain English. The agent will autonomously verify against
          DRAP, find alternatives, surface enforcement history, and produce your complaint
          letter — you watch every step live.
        </p>
      </section>

      <StructuredReportForm onSubmit={investigate} disabled={status === 'streaming'} />

      {status === 'error' && (
        <div className="card border-l-4 border-red-500">
          <div className="font-medium text-red-700">Agent failed</div>
          <div className="mt-1 text-sm text-slate-700">
            {errorMessage || 'Something went wrong.'}
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Common causes: <code>GEMINI_API_KEY</code> not set in <code>backend/.env</code>,
            backend not running on <code>:8000</code>, or rate limit on the Gemini API.
          </div>
          <button onClick={reset} className="btn-secondary mt-3 text-xs">
            Try again
          </button>
        </div>
      )}

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
