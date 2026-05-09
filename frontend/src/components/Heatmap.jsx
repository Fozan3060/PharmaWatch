import { AdvancedMarker, APIProvider, InfoWindow, Map, Pin } from '@vis.gl/react-google-maps';
import { useState } from 'react';

import { coordsFor, PAKISTAN_CENTER } from '../lib/cityCoords.js';
import { pct, SEVERITY_BG, SEVERITY_LABEL } from '../lib/format.js';
import HeatmapFallback from './HeatmapFallback.jsx';

const COLOR = {
  clean: '#22c55e',
  watch: '#facc15',
  suspicious: '#f97316',
  confirmed: '#ef4444',
};

export default function Heatmap({ pharmacies }) {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

  if (!apiKey) {
    return <HeatmapFallback pharmacies={pharmacies} />;
  }

  return (
    <APIProvider apiKey={apiKey}>
      <div className="h-[480px] w-full overflow-hidden rounded-lg border border-slate-200 shadow-sm">
        <Map
          defaultCenter={PAKISTAN_CENTER}
          defaultZoom={5.5}
          mapId="pharmawatch-map"
          gestureHandling="greedy"
          disableDefaultUI={false}
        >
          {pharmacies.map((p) => (
            <Marker key={p.pharmacy_id} pharmacy={p} />
          ))}
        </Map>
      </div>
    </APIProvider>
  );
}

function Marker({ pharmacy }) {
  const [open, setOpen] = useState(false);
  const pos = coordsFor(pharmacy.city, pharmacy.area);
  return (
    <>
      <AdvancedMarker position={pos} onClick={() => setOpen((o) => !o)}>
        <Pin background={COLOR[pharmacy.classification] || '#94a3b8'} borderColor="#0b3954" glyphColor="#0b3954" />
      </AdvancedMarker>
      {open && (
        <InfoWindow position={pos} onCloseClick={() => setOpen(false)}>
          <div className="min-w-[220px] space-y-1 text-sm">
            <div className="font-semibold text-brand-500">{pharmacy.pharmacy_name}</div>
            <div className="text-slate-600">
              {[pharmacy.area, pharmacy.city].filter(Boolean).join(', ')}
            </div>
            <div className="flex items-center justify-between pt-2">
              <span className={`badge ${SEVERITY_BG[pharmacy.classification] || 'bg-slate-200'}`}>
                {SEVERITY_LABEL[pharmacy.classification] || pharmacy.classification}
              </span>
              <span className="text-xs font-medium text-slate-700">
                {pharmacy.report_count} report{pharmacy.report_count === 1 ? '' : 's'} (30d)
              </span>
            </div>
            {pharmacy.medicines_flagged?.length > 0 && (
              <div className="pt-1 text-xs text-slate-600">
                Flagged: {pharmacy.medicines_flagged.slice(0, 3).join(', ')}
                {pharmacy.medicines_flagged.length > 3 ? '…' : ''}
              </div>
            )}
            <div className="pt-1 text-xs text-slate-500">
              Avg overcharge: {pct(pharmacy.avg_overcharge_pct)}
            </div>
          </div>
        </InfoWindow>
      )}
    </>
  );
}
