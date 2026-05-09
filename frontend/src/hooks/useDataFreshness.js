import { useEffect, useState } from 'react';

import { fetchHealth } from '../lib/api.js';

export default function useDataFreshness() {
  const [data, setData] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetchHealth()
      .then((h) => !cancelled && setData(h))
      .catch(() => !cancelled && setData(null));
    return () => {
      cancelled = true;
    };
  }, []);

  return data;
}
