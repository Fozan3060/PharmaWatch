// Tiny shared skeleton primitives. Inline animation, no extra deps.

export function SkeletonBlock({ className = '' }) {
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

export function ReportSkeleton() {
  return (
    <div className="space-y-4">
      <SkeletonBlock className="h-6 w-56" />
      <div className="card space-y-3">
        <SkeletonBlock className="h-4 w-32" />
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <SkeletonBlock className="h-12" />
          <SkeletonBlock className="h-12" />
          <SkeletonBlock className="h-12" />
          <SkeletonBlock className="h-12" />
        </div>
      </div>
      <div className="card space-y-3">
        <SkeletonBlock className="h-4 w-48" />
        <SkeletonBlock className="h-3 w-full" />
        <SkeletonBlock className="h-3 w-3/4" />
      </div>
    </div>
  );
}
