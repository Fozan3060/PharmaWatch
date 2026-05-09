import AgentTracePanel from '../components/AgentTracePanel.jsx';
import InvestigationReport from '../components/InvestigationReport.jsx';
import ReportForm from '../components/ReportForm.jsx';
import useAgentStream from '../hooks/useAgentStream.js';

export default function InvestigatePage() {
  const { events, status, errorMessage, investigate, reset } = useAgentStream();

  return (
    <div className="space-y-6">
      <section className="space-y-1">
        <h1 className="text-3xl">Investigate a complaint</h1>
        <p className="max-w-3xl text-sm text-slate-600">
          Describe what happened in plain English. The agent will autonomously verify against
          DRAP, find alternatives, surface enforcement history, and produce your complaint
          letter — you watch every tool call live.
        </p>
      </section>

      <ReportForm onSubmit={investigate} disabled={status === 'streaming'} />

      {status === 'error' && (
        <div className="card border-l-4 border-red-500 text-sm text-red-700">
          {errorMessage || 'Something went wrong.'}
          <button onClick={reset} className="ml-3 text-xs underline">
            try again
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_360px]">
        <div className="space-y-6">
          <InvestigationReport events={events} />
        </div>
        <aside>
          <AgentTracePanel events={events} status={status} />
        </aside>
      </div>
    </div>
  );
}
