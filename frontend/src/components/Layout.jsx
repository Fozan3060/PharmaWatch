import { Link, NavLink } from 'react-router-dom';

import useDataFreshness from '../hooks/useDataFreshness.js';
import { shortDate } from '../lib/format.js';

const linkClass = ({ isActive }) =>
  `text-sm font-medium px-3 py-2 rounded-md ${
    isActive ? 'bg-brand-500 text-white' : 'text-slate-700 hover:bg-slate-100'
  }`;

export default function Layout({ children }) {
  const health = useDataFreshness();
  const drapTable = health?.data_freshness?.medicines;
  const enforcementTable = health?.data_freshness?.local_drap_enforcement;
  const newest =
    drapTable?.last_scraped_at &&
    enforcementTable?.last_scraped_at &&
    (drapTable.last_scraped_at > enforcementTable.last_scraped_at
      ? drapTable.last_scraped_at
      : enforcementTable.last_scraped_at);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <Link to="/" className="flex items-center gap-2 text-brand-500">
            <span className="text-xl font-bold tracking-tight">PharmaWatch</span>
            <span className="hidden rounded-full bg-brand-50 px-2 py-0.5 text-xs font-semibold text-brand-500 sm:inline">
              Beta
            </span>
          </Link>
          <nav className="flex items-center gap-1">
            <NavLink to="/" end className={linkClass}>
              Heatmap
            </NavLink>
            <NavLink to="/investigate" className={linkClass}>
              Investigate
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6">{children}</main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-4 py-4 text-xs text-slate-500 sm:flex-row">
          <div>Built with purpose. Powered by DRAP&rsquo;s public data. Anonymous by design.</div>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            {newest && <span>DRAP data current as of <strong>{shortDate(newest)}</strong></span>}
            {!health && <span>checking data freshness…</span>}
            <span className="text-slate-400">|</span>
            <span title="Real-time inventory not available — DRAP has no public stock API for Pakistani pharmacies.">
              ⓘ Real-time inventory not available
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
