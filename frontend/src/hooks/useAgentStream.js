import { useCallback, useState } from 'react';

import { streamInvestigation } from '../lib/api.js';

const TERMINAL = new Set(['final', 'error']);

export default function useAgentStream() {
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState('idle'); // idle | streaming | done | error
  const [errorMessage, setErrorMessage] = useState(null);

  const investigate = useCallback(async (userInput) => {
    setEvents([]);
    setErrorMessage(null);
    setStatus('streaming');
    try {
      for await (const evt of streamInvestigation(userInput)) {
        setEvents((prev) => [...prev, evt]);
        if (TERMINAL.has(evt.event)) {
          setStatus(evt.event === 'final' ? 'done' : 'error');
          if (evt.event === 'error') {
            setErrorMessage(evt.data?.reason || 'Agent failed.');
          }
        }
      }
      setStatus((prev) => (prev === 'streaming' ? 'done' : prev));
    } catch (err) {
      setStatus('error');
      setErrorMessage(err.message);
    }
  }, []);

  const reset = useCallback(() => {
    setEvents([]);
    setStatus('idle');
    setErrorMessage(null);
  }, []);

  return { events, status, errorMessage, investigate, reset };
}
