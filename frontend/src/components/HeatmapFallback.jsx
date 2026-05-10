import { pct, SEVERITY_BG, SEVERITY_LABEL } from '../lib/format.js';

// Used when no Google Maps API key is configured. Renders the same data
// as a sortable list so the heatmap page is never broken in dev.
export default function HeatmapFallback({ pharmacies }) {
  return (
    <div className="card">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h3 className="text-base">Flagged pharmacies (last 30 days)</h3>
          <p className="text-xs text-slate-500">
            Map view requires <code>VITE_GOOGLE_MAPS_API_KEY</code> in <code>.env</code>.
          </p>
        </div>
      </div>
      <ul className="divide-y divide-slate-200">
        {pharmacies.length === 0 && (
          <li className="py-4 text-sm text-slate-500">No reports in the last 30 days.</li>
        )}
        {pharmacies.map((p) => (
          <li key={p.pharmacy_id} className="flex items-center justify-between py-3">
            <div>
              <div className="font-medium">{p.pharmacy_name}</div>
              <div className="text-xs text-slate-500">
                {[p.area, p.city].filter(Boolean).join(', ')}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-500">avg {pct(p.avg_overcharge_pct)}</span>
              <span className="text-xs font-medium">
                {p.report_count} report{p.report_count === 1 ? '' : 's'}
              </span>
              <span className={`badge ${SEVERITY_BG[p.classification] || 'bg-slate-200'}`}>
                {SEVERITY_LABEL[p.classification] || p.classification}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
