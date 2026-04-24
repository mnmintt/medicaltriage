import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import ClinicalShell from '../components/ClinicalShell';
import ExplanationCard from '../components/ExplanationCard';
import SwarmPanel from '../components/SwarmPanel';
import { getPatient, getQueueStats } from '../api';

export default function PatientDisplayPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const [patientData, queueData] = await Promise.all([getPatient(id), getQueueStats()]);
      setPatient(patientData);
      setStats(queueData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const timer = setInterval(load, 10000);
    return () => clearInterval(timer);
  }, [id]);

  if (loading) {
    return (
      <ClinicalShell active="Kiosk" sideAction={<button className="btn-black" onClick={() => navigate('/kiosk')} style={{ width: '100%' }}>New Intake</button>}>
        <div className="canvas-narrow"><div className="panel" style={{ padding: 30 }}>Loading triage record...</div></div>
      </ClinicalShell>
    );
  }

  if (!patient) {
    return (
      <ClinicalShell active="Kiosk" sideAction={<button className="btn-black" onClick={() => navigate('/kiosk')} style={{ width: '100%' }}>New Intake</button>}>
        <div className="canvas-narrow"><div className="panel" style={{ padding: 30 }}>Patient not found.</div></div>
      </ClinicalShell>
    );
  }

  const result = patient.triage_result;
  const waitRange = `${Math.max(result.estimated_wait_minutes - 10, 0)}-${result.estimated_wait_minutes} min`;
  const ahead = Math.max((result.queue_position || 1) - 1, 0);

  return (
    <ClinicalShell active="Kiosk" sideAction={<button className="btn-black" onClick={() => navigate('/kiosk')} style={{ width: '100%' }}>New Intake</button>}>
      <div className="canvas-narrow" style={{ display: 'grid', gap: 22 }}>
        <div style={{ textAlign: 'center' }}>
          <div className="zone-ring" style={{ borderColor: `var(--zone-${result.zone})`, color: `var(--zone-${result.zone})`, background: `color-mix(in srgb, var(--zone-${result.zone}) 10%, transparent)` }}>{result.zone}</div>
          <div className="zone-ring-label" style={{ color: `var(--zone-${result.zone})` }}>{result.zone_label.toUpperCase()}</div>
          <h2 className="section-title" style={{ fontSize: 40 }}>Triage Assessment Complete</h2>
        </div>

        <div className="stat-grid">
          <div className="stat-pill">
            <div className="stat-pill-value">{waitRange}</div>
            <div className="stat-pill-label">EST. WAITING TIME</div>
          </div>
          <div className="stat-pill">
            <div className="stat-pill-value">{result.queue_position} of {stats?.total_patients || result.queue_position}</div>
            <div className="stat-pill-label">QUEUE POSITION</div>
          </div>
          <div className="stat-pill">
            <div className="stat-pill-value green">{ahead} ahead</div>
            <div className="stat-pill-label">PRIORITY FLOW</div>
          </div>
        </div>

        <ExplanationCard explanation={result.explanation} zone={result.zone} />

        <div className="panel" style={{ padding: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', borderTop: '1px solid var(--border-soft)', paddingTop: 8 }}>
            <div>
              <div className="kv-label">Patient Record</div>
              <div style={{ fontFamily: 'Public Sans, sans-serif', fontWeight: 700, fontSize: 28, color: 'var(--text-title)' }}>
                {patient.name || 'Unnamed Patient'}
              </div>
              <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, color: 'var(--text-body)' }}>ID: {patient.id}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div className="kv-label">Vital Check</div>
              <div style={{ fontFamily: 'IBM Plex Mono, monospace', color: 'var(--accent-green)', fontSize: 14, fontWeight: 600 }}>STABLE</div>
            </div>
          </div>
        </div>

        <SwarmPanel triageResult={result} />

        <div style={{ display: 'flex', justifyContent: 'center', gap: 16 }}>
          <button className="btn-black" onClick={load}>Refresh Status</button>
          <button className="btn-link" onClick={() => window.print()}>Print Ticket</button>
        </div>
      </div>
    </ClinicalShell>
  );
}
