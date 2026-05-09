import { useState } from 'react';
import clsx from 'clsx';

const ICON = {
  started: '▶',
  thinking: '💭',
  tool_call: '⚙️',
  tool_result: '✓',
  tool_error: '✗',
  final: '🏁',
  error: '⚠️',
};

const ROW_BG = {
  tool_call: 'bg-slate-50',
  tool_result: 'bg-green-50',
  tool_error: 'bg-red-50',
  final: 'bg-brand-50',
  error: 'bg-red-50',
};

export default function AgentTracePanel({ events, status }) {
  if (events.length === 0 && status === 'idle') return null;

  return (
    <div className="card">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-base">Agent trace</h3>
        <span className="text-xs text-slate-500">
          {status === 'streaming' && 'streaming…'}
          {status === 'done' && `${events.length} events`}
          {status === 'error' && 'failed'}
        </span>
      </div>
      <ol className="space-y-1 text-sm">
        {events.map((evt, idx) => (
          <TraceRow key={idx} evt={evt} />
        ))}
        {status === 'streaming' && (
          <li className="flex items-center gap-2 px-2 py-1 text-xs text-slate-500">
            <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-brand-500" />
            agent thinking…
          </li>
        )}
      </ol>
    </div>
  );
}

function TraceRow({ evt }) {
  const [open, setOpen] = useState(false);
  const expandable = evt.event === 'tool_call' || evt.event === 'tool_result' || evt.event === 'tool_error';
  return (
    <li className={clsx('rounded px-2 py-1', ROW_BG[evt.event])}>
      <button
        type="button"
        onClick={() => expandable && setOpen((o) => !o)}
        className={clsx(
          'flex w-full items-center gap-2 text-left',
          expandable ? 'cursor-pointer' : 'cursor-default',
        )}
      >
        <span className="w-5 text-center">{ICON[evt.event] || '·'}</span>
        <span className="font-medium">{labelFor(evt)}</span>
        {expandable && (
          <span className="ml-auto text-xs text-slate-400">{open ? 'hide' : 'expand'}</span>
        )}
      </button>
      {expandable && open && (
        <pre className="mt-2 overflow-x-auto rounded bg-white p-2 text-xs text-slate-700 ring-1 ring-slate-200">
{JSON.stringify(payloadFor(evt), null, 2)}
        </pre>
      )}
      {(evt.event === 'thinking' || evt.event === 'final' || evt.event === 'error') && (
        <div className="mt-1 whitespace-pre-wrap pl-7 text-xs text-slate-700">
          {evt.data?.text || evt.data?.reason || evt.data?.error || JSON.stringify(evt.data)}
        </div>
      )}
    </li>
  );
}

function labelFor(evt) {
  switch (evt.event) {
    case 'started':
      return 'Started';
    case 'thinking':
      return 'Agent thinking';
    case 'tool_call':
      return `Calling: ${evt.data?.name}`;
    case 'tool_result':
      return `${evt.data?.name} returned`;
    case 'tool_error':
      return `${evt.data?.name} errored`;
    case 'final':
      return 'Final summary';
    case 'error':
      return 'Agent error';
    default:
      return evt.event;
  }
}

function payloadFor(evt) {
  if (evt.event === 'tool_call') return evt.data?.args || {};
  if (evt.event === 'tool_result') return evt.data?.result || {};
  if (evt.event === 'tool_error') return { error: evt.data?.error };
  return evt.data;
}
