import { useState } from 'react';

import { submitCommunityReport } from '../lib/api.js';
import { rupees, SEVERITY_BG, SEVERITY_LABEL } from '../lib/format.js';

// Visible only when a verified overcharge exists. The user reviews the
// report data the agent assembled, then explicitly clicks Submit. The
// agent never auto-logs accusations.

export default function SubmitToCommunity({ incident }) {
  const [state, setState] = useState({ phase: 'idle' });

  if (!incident) return null;

  const payload = {
    pharmacy_name: incident.pharmacy_name,
    pharmacy_area: incident.pharmacy_area,
    pharmacy_city: incident.pharmacy_city,
    medicine: [incident.medicine_name, incident.strength].filter(Boolean).join(' '),
    official_mrp_pkr: incident.official_mrp_pkr,
    charged_price_pkr: incident.charged_price_pkr,
  };

  async function handleSubmit() {
    setState({ phase: 'submitting' });
    try {
      const result = await submitCommunityReport(payload);
      setState({ phase: 'done', result });
    } catch (err) {
      setState({ phase: 'error', error: err.message });
    }
  }

  if (state.phase === 'done') {
    const cls = state.result.classification;
    return (
      <div className="card border-l-4 border-green-500">
        <h3 className="text-base text-green-700">✓ Submitted to community heatmap</h3>
        <p className="mt-2 text-sm text-slate-700">
          Thanks for contributing. This pharmacy now has{' '}
          <strong>{state.result.pharmacy_total_reports_30d}</strong> verified report
          {state.result.pharmacy_total_reports_30d === 1 ? '' : 's'} in the last 30 days.
        </p>
        <div className="mt-2">
          <span className={`badge ${SEVERITY_BG[cls]}`}>
            Now classified: {SEVERITY_LABEL[cls] || cls}
          </span>
        </div>
        {cls === 'confirmed' && (
          <p className="mt-2 text-xs text-red-700">
            10+ reports threshold crossed — this pharmacy is now eligible for a collective
            DRAP dossier. Refresh the heatmap to see the red marker.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="card border-l-4 border-brand-500">
      <h3 className="text-base">Submit this report to the community heatmap</h3>
      <p className="mt-1 text-xs text-slate-500">
        Anonymous — no PII is stored. The agent has already verified the overcharge against
        DRAP. Your submission helps build a collective evidence base; once 10+ reports
        accumulate against the same pharmacy, the agent can generate a bulk DRAP dossier.
      </p>

      <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 rounded bg-slate-50 p-3 text-xs">
        <div>
          <dt className="text-slate-500">Pharmacy</dt>
          <dd className="font-medium text-slate-800">
            {payload.pharmacy_name}
            {payload.pharmacy_area && `, ${payload.pharmacy_area}`}, {payload.pharmacy_city}
          </dd>
        </div>
        <div>
          <dt className="text-slate-500">Medicine</dt>
          <dd className="font-medium text-slate-800">{payload.medicine}</dd>
        </div>
        <div>
          <dt className="text-slate-500">DRAP MRP</dt>
          <dd className="font-medium text-slate-800">{rupees(payload.official_mrp_pkr)}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Charged</dt>
          <dd className="font-medium text-slate-800">{rupees(payload.charged_price_pkr)}</dd>
        </div>
      </dl>

      {state.phase === 'error' && (
        <div className="mt-3 rounded bg-red-50 p-2 text-xs text-red-700">{state.error}</div>
      )}

      <button
        onClick={handleSubmit}
        disabled={state.phase === 'submitting'}
        className="btn-primary mt-3"
      >
        {state.phase === 'submitting' ? 'Submitting…' : '📍 Submit to community heatmap'}
      </button>
    </div>
  );
}
