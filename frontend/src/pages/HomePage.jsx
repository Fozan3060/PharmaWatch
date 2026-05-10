import { Link } from 'react-router-dom';

import Heatmap from '../components/Heatmap.jsx';
import { HeatmapSkeleton } from '../components/Skeleton.jsx';
import useHeatmap from '../hooks/useHeatmap.js';

export default function HomePage() {
  const { pharmacies, loading, error } = useHeatmap();

  const stats = {
    confirmed: pharmacies.filter((p) => p.classification === 'confirmed').length,
    suspicious: pharmacies.filter((p) => p.classification === 'suspicious').length,
    watch: pharmacies.filter((p) => p.classification === 'watch').length,
    totalReports: pharmacies.reduce((sum, p) => sum + (p.report_count || 0), 0),
  };

  return (
    <div className="space-y-8">
      <Hero stats={stats} />

      {error && (
        <div className="card border-l-4 border-red-500 text-sm text-red-700">
          Could not load heatmap: {error}
        </div>
      )}

      {loading ? <HeatmapSkeleton /> : <Heatmap pharmacies={pharmacies} />}

      <Legend />
    </div>
  );
}

function Hero({ stats }) {
  return (
    <section className="rounded-xl bg-gradient-to-br from-brand-500 via-brand-600 to-brand-700 p-8 text-white shadow-md">
      <div className="grid gap-6 md:grid-cols-[1.5fr_1fr] md:items-center">
        <div className="space-y-3">
          <h1 className="text-3xl font-bold leading-tight text-white sm:text-4xl">
            Pakistan&rsquo;s pharmacy fraud heatmap.
          </h1>
          <p className="max-w-prose text-sm text-brand-50/90 sm:text-base">
            Every dot is a pharmacy with verified community reports of overcharging in the
            last 30 days. The agentic AI cross-checks every claim against DRAP&rsquo;s
            registered Maximum Retail Prices and surfaces prior enforcement actions —
            anonymous by design.
          </p>
          <div className="pt-1">
            <Link to="/investigate" className="btn bg-white text-brand-600 hover:bg-brand-50">
              I was overcharged →
            </Link>
          </div>
        </div>
        <dl className="grid grid-cols-2 gap-3">
          <Stat label="Confirmed" value={stats.confirmed} colorClass="bg-severity-confirmed" />
          <Stat label="Suspicious" value={stats.suspicious} colorClass="bg-severity-suspicious" />
          <Stat label="Watchlist" value={stats.watch} colorClass="bg-severity-watch text-slate-900" />
          <Stat label="Total reports (30d)" value={stats.totalReports} colorClass="bg-white/15" />
        </dl>
      </div>
    </section>
  );
}

function Stat({ label, value, colorClass }) {
  return (
    <div className={`rounded-lg ${colorClass} px-4 py-3`}>
      <dd className="text-2xl font-bold leading-none">{value}</dd>
      <dt className="mt-1 text-xs uppercase tracking-wide opacity-90">{label}</dt>
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
