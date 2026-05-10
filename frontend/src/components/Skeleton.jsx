// Tiny shared skeleton primitives. Inline animation, no extra deps.

function SkeletonBlock({ className = '' }) {
  return <div className={`animate-pulse rounded bg-slate-200 ${className}`} />;
}

export function HeatmapSkeleton() {
  return (
    <div className="card flex h-[480px] items-center justify-center">
      <div className="space-y-3 text-center">
        <SkeletonBlock className="mx-auto h-3 w-40" />
        <SkeletonBlock className="mx-auto h-3 w-24" />
        <div className="text-xs text-slate-400">Loading 30-day fraud reports…</div>
      </div>
    </div>
  );
}
