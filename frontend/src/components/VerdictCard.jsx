import { pct, rupees } from '../lib/format.js';

// Big, unambiguous verdict at the top of the Investigation Report.
// `incident` is the structured object the agent passed to generate_complaint_letter
// (or extracted from drap_price_lookup if no overcharge was found).

export default function VerdictCard({ incident }) {
  if (!incident) return null;

  const { charged_price_pkr, official_mrp_pkr, overcharge_amt_pkr, overcharge_pct, medicine_name, strength } = incident;
  const overcharged = charged_price_pkr != null && official_mrp_pkr != null && charged_price_pkr > official_mrp_pkr;
  const medicineLabel = [medicine_name, strength].filter(Boolean).join(' ');

  if (overcharged) {
    return (
      <div className="rounded-xl border-2 border-red-500 bg-red-50 p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <span className="text-3xl">🚨</span>
          <div>
            <div className="text-xs font-semibold uppercase tracking-wide text-red-700">
              Verdict
            </div>
            <h2 className="text-2xl font-bold text-red-700 sm:text-3xl">
              You were overcharged.
            </h2>
          </div>
        </div>
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          <Stat label="Overcharged by" value={rupees(overcharge_amt_pkr)} highlight />
          <Stat label="That's" value={`${pct(overcharge_pct)} above MRP`} />
          <Stat label="On" value={medicineLabel} />
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-1 text-sm text-red-900">
          <span>You paid: <strong>{rupees(charged_price_pkr)}</strong></span>
          <span>DRAP MRP: <strong>{rupees(official_mrp_pkr)}</strong></span>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border-2 border-green-500 bg-green-50 p-6 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="text-3xl">✅</span>
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-green-700">
            Verdict
          </div>
          <h2 className="text-2xl font-bold text-green-700 sm:text-3xl">
            Price within DRAP MRP.
          </h2>
        </div>
      </div>
      <p className="mt-3 text-sm text-green-900">
        DRAP-registered MRP for {medicineLabel || 'this medicine'} is{' '}
        <strong>{rupees(official_mrp_pkr)}</strong>. The price you reported is at or below
        this — no overcharge to report.
      </p>
    </div>
  );
}

function Stat({ label, value, highlight }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-red-700/80">{label}</div>
      <div className={`mt-0.5 truncate font-bold text-red-700 ${highlight ? 'text-2xl' : 'text-xl'}`}>
        {value}
      </div>
    </div>
  );
}
