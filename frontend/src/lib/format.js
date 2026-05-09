export function rupees(n) {
  if (n == null) return '—';
  return `Rs. ${Math.round(Number(n)).toLocaleString('en-PK')}`;
}

export function pct(n) {
  if (n == null) return '—';
  return `${Number(n).toFixed(1)}%`;
}

export function shortDate(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}

export const SEVERITY_LABEL = {
  clean: 'Clean',
  watch: 'Watch',
  suspicious: 'Suspicious',
  confirmed: 'Confirmed',
  critical: 'Critical',
};

export const SEVERITY_BG = {
  clean: 'bg-severity-clean text-white',
  watch: 'bg-severity-watch text-slate-900',
  suspicious: 'bg-severity-suspicious text-white',
  confirmed: 'bg-severity-confirmed text-white',
  critical: 'bg-severity-critical text-white',
};
