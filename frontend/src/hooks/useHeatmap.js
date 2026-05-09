import { collection, onSnapshot, query, where } from 'firebase/firestore';
import { useEffect, useState } from 'react';

import { fetchHeatmap } from '../lib/api.js';
import { getDb, isFirebaseConfigured } from '../lib/firebase.js';

export default function useHeatmap() {
  const [pharmacies, setPharmacies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    let unsub = null;

    async function load() {
      try {
        const data = await fetchHeatmap();
        if (cancelled) return;
        setPharmacies(data.pharmacies || []);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();

    if (isFirebaseConfigured()) {
      const db = getDb();
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - 30);
      const q = query(collection(db, 'community_reports'), where('timestamp', '>=', cutoff));
      // On any change, refetch the server-aggregated heatmap.
      unsub = onSnapshot(q, () => {
        if (!cancelled) load();
      });
    }

    return () => {
      cancelled = true;
      if (unsub) unsub();
    };
  }, []);

  return { pharmacies, loading, error };
}
