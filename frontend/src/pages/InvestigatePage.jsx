import AgentTracePanel from '../components/AgentTracePanel.jsx';
import InvestigationReport from '../components/InvestigationReport.jsx';
import ReportForm from '../components/ReportForm.jsx';
import { ReportSkeleton } from '../components/Skeleton.jsx';
import useAgentStream from '../hooks/useAgentStream.js';

export default function InvestigatePage() {
  const { events, status, errorMessage, investigate, reset } = useAgentStream();
  const isStreaming = status === 'streaming';
  const hasNoFindingsYet = events.length === 0 || !events.some((e) => e.event === 'tool_result');

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

      <ReportForm onSubmit={investigate} disabled={isStreaming} />

      {status === 'error' && (
        <div className="card border-l-4 border-red-500 text-sm text-red-700">
          <div className="font-medium">Agent failed.</div>
          <div className="mt-1 text-xs">
            {errorMessage || 'Something went wrong — check that GEMINI_API_KEY is set in backend/.env.'}
          </div>
          <button onClick={reset} className="mt-2 text-xs underline">
            try again
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_360px]">
        <div className="space-y-6">
          {isStreaming && hasNoFindingsYet ? (
            <ReportSkeleton />
          ) : (
            <InvestigationReport events={events} />
          )}
        </div>
        <aside>
          <AgentTracePanel events={events} status={status} />
        </aside>
      </div>
    </div>
  );
}
