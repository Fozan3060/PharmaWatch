import { Link } from 'react-router-dom';

import Heatmap from '../components/Heatmap.jsx';
import useHeatmap from '../hooks/useHeatmap.js';

export default function HomePage() {
  const { pharmacies, loading, error } = useHeatmap();

  return (
    <div className="space-y-6">
      <section className="space-y-2">
        <h1 className="text-3xl">Pakistan&rsquo;s pharmacy fraud heatmap</h1>
        <p className="max-w-3xl text-sm text-slate-600">
          Every dot is a pharmacy with verified community reports of overcharging in the last
          30 days. Click a marker for incident details. New reports update the map in real
          time via Firebase.
        </p>
      </section>

      {error && (
        <div className="card border-l-4 border-red-500 text-sm text-red-700">
          Could not load heatmap: {error}
        </div>
      )}

      {loading ? (
        <div className="card text-sm text-slate-500">Loading heatmap…</div>
      ) : (
        <Heatmap pharmacies={pharmacies} />
      )}

      <section className="card">
        <h3 className="text-base">Got overcharged?</h3>
        <p className="mt-1 text-sm text-slate-600">
          The PharmaWatch agent will verify the price against DRAP, find cheaper generic
          alternatives, surface any prior violations on the pharmacy, and prepare a formal
          complaint letter. Anonymous by design.
        </p>
        <Link to="/investigate" className="btn-primary mt-3">
          Investigate a complaint
        </Link>
      </section>

      <Legend />
    </div>
  );
}

function Legend() {
  return (
    <div className="card">
      <h3 className="text-base">Map legend</h3>
      <ul className="mt-2 grid grid-cols-2 gap-2 text-xs text-slate-700 sm:grid-cols-4">
        <LegendDot color="#facc15" label="Watch (1–3 reports)" />
        <LegendDot color="#f97316" label="Suspicious (4–9)" />
        <LegendDot color="#ef4444" label="Confirmed (10+)" />
        <LegendDot color="#94a3b8" label="No reports yet" />
      </ul>
    </div>
  );
}

function LegendDot({ color, label }) {
  return (
    <li className="flex items-center gap-2">
      <span className="inline-block h-3 w-3 rounded-full" style={{ background: color }} />
      <span>{label}</span>
    </li>
  );
}
