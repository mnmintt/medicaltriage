const API_BASE = '/api';

export async function submitTriage(data) {
  const res = await fetch(`${API_BASE}/triage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getPatients() {
  const res = await fetch(`${API_BASE}/patients`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getPatient(id) {
  const res = await fetch(`${API_BASE}/patients/${id}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function overrideZone(id, newZone, reason) {
  const res = await fetch(`${API_BASE}/patients/${id}/override`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ new_zone: newZone, reason }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function dischargePatient(id) {
  const res = await fetch(`${API_BASE}/patients/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getQueueStats() {
  const res = await fetch(`${API_BASE}/queue-stats`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
