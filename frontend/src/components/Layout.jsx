import { Link, NavLink } from 'react-router-dom';

const linkClass = ({ isActive }) =>
  `text-sm font-medium px-3 py-2 rounded-md ${
    isActive ? 'bg-brand-500 text-white' : 'text-slate-700 hover:bg-slate-100'
  }`;

export default function Layout({ children }) {
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
        <div className="mx-auto max-w-7xl px-4 py-4 text-center text-xs text-slate-500">
          Built with purpose. Powered by DRAP&rsquo;s public data. Anonymous by design.
        </div>
      </footer>
    </div>
  );
}
