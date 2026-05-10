// Backend API wrappers. Dev mode uses the Vite proxy (/agent etc.); production
// uses VITE_API_BASE_URL.

const BASE = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchHealth() {
  const res = await fetch(`${BASE}/health`);
  if (!res.ok) throw new Error(`health failed: ${res.status}`);
  return res.json();
}

export async function searchMedicines(q, limit = 10) {
  const res = await fetch(`${BASE}/medicines/search?q=${encodeURIComponent(q)}&limit=${limit}`);
  if (!res.ok) throw new Error(`medicines/search failed: ${res.status}`);
  const body = await res.json();
  return body.results;
}

export async function searchPharmacies(q, city, limit = 10) {
  const params = new URLSearchParams({ q, limit: String(limit) });
  if (city) params.set('city', city);
  const res = await fetch(`${BASE}/pharmacies/known?${params.toString()}`);
  if (!res.ok) throw new Error(`pharmacies/known failed: ${res.status}`);
  const body = await res.json();
  return body.results;
}

export async function fetchHeatmap() {
  const res = await fetch(`${BASE}/reports/heatmap`);
  if (!res.ok) throw new Error(`heatmap failed: ${res.status}`);
  return res.json();
}

export async function submitCommunityReport(report) {
  const res = await fetch(`${BASE}/reports/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(report),
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`submit failed (${res.status}): ${body || res.statusText}`);
  }
  return res.json();
}

export async function downloadComplaintPdf(complaint) {
  const res = await fetch(`${BASE}/complaint/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(complaint),
  });
  if (!res.ok) throw new Error(`complaint pdf failed: ${res.status}`);
  return res.blob();
}

export async function downloadDossierPdf(dossier) {
  const res = await fetch(`${BASE}/dossier/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dossier),
  });
  if (!res.ok) throw new Error(`dossier pdf failed: ${res.status}`);
  return res.blob();
}

// Stream the agent investigation. Yields parsed SSE events as they arrive.
export async function* streamInvestigation(userInput) {
  const res = await fetch(`${BASE}/agent/investigate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput }),
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`investigate failed (${res.status}): ${body || res.statusText}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sep;
    while ((sep = buffer.indexOf('\n\n')) !== -1) {
      const raw = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      const parsed = parseSseEvent(raw);
      if (parsed) yield parsed;
    }
  }
}

function parseSseEvent(raw) {
  let event = 'message';
  const dataLines = [];
  let id = null;
  for (const line of raw.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim();
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trimStart());
    else if (line.startsWith('id:')) id = line.slice(3).trim();
  }
  if (dataLines.length === 0) return null;
  try {
    return { event, id, data: JSON.parse(dataLines.join('\n')) };
  } catch {
    return { event, id, data: dataLines.join('\n') };
  }
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
