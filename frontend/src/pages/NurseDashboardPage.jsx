import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ClinicalShell from '../components/ClinicalShell';
import ZoneBadge from '../components/ZoneBadge';
import SwarmPanel from '../components/SwarmPanel';
import { dischargePatient, getPatients, getQueueStats, overrideZone } from '../api';

export default function NurseDashboardPage() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [stats, setStats] = useState(null);
  const [selected, setSelected] = useState(null);
  const [overrideModal, setOverrideModal] = useState(null);
  const [overrideForm, setOverrideForm] = useState({ zone: 1, reason: '' });

  const fetchData = async () => {
    const [patientData, queueData] = await Promise.all([getPatients(), getQueueStats()]);
    setPatients(patientData);
    setStats(queueData);
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, 5000);
    return () => clearInterval(timer);
  }, []);

  const activePatients = patients.filter((p) => p.status === 'waiting');

  const submitOverride = async () => {
    if (!overrideModal || !overrideForm.reason) return;
    await overrideZone(overrideModal, overrideForm.zone, overrideForm.reason);
    setOverrideModal(null);
    setOverrideForm({ zone: 1, reason: '' });
    fetchData();
  };

  const doDischarge = async (id) => {
    await dischargePatient(id);
    fetchData();
  };

  return (
    <ClinicalShell active="Dashboard" sideAction={<button className="btn-black" onClick={() => navigate('/kiosk')} style={{ width: '100%' }}>New Intake</button>}>
      <div className="canvas-wide" style={{ display: 'grid', gap: 16 }}>
        <div className="panel" style={{ padding: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ fontSize: 30 }}>Nurse Dashboard</h2>
              <p style={{ color: 'var(--text-soft)', fontSize: 14 }}>Live triage queue and override controls.</p>
            </div>
            <button className="btn-black" onClick={fetchData}>Refresh</button>
          </div>
        </div>

        {stats ? (
          <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(4, minmax(0, 1fr))' }}>
            <SimpleStat label="Total" value={stats.total_patients} />
            <SimpleStat label="Zone 1" value={stats.zone_counts[1] || 0} />
            <SimpleStat label="Zone 2" value={stats.zone_counts[2] || 0} />
            <SimpleStat label="Flagged" value={stats.flagged_count} />
          </div>
        ) : null}

        <div className="panel" style={{ padding: 16 }}>
          <h3 style={{ fontSize: 20, marginBottom: 12 }}>Active Patients ({activePatients.length})</h3>
          <div style={{ display: 'grid', gap: 8 }}>
            {activePatients.map((patient) => (
              <div key={patient.id} className="panel-soft" style={{ padding: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 14 }}>{patient.id}</span>
                    <ZoneBadge zone={patient.effective_zone} size="sm" />
                    <span style={{ color: 'var(--text-soft)', fontSize: 12 }}>Confidence: {patient.triage_result.confidence}%</span>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button className="btn-muted" onClick={() => setSelected((id) => (id === patient.id ? null : patient.id))}>Swarm</button>
                    <button className="btn-muted" onClick={() => { setOverrideModal(patient.id); setOverrideForm({ zone: patient.effective_zone, reason: '' }); }}>Override</button>
                    <button className="btn-muted" onClick={() => navigate(`/display/${patient.id}`)}>View</button>
                    <button className="btn-black" onClick={() => doDischarge(patient.id)}>Discharge</button>
                  </div>
                </div>
                {selected === patient.id ? <div style={{ marginTop: 10 }}><SwarmPanel triageResult={patient.triage_result} /></div> : null}
              </div>
            ))}
            {activePatients.length === 0 ? <div style={{ color: 'var(--text-soft)', fontSize: 14 }}>No active patients in queue.</div> : null}
          </div>
        </div>
      </div>

      {overrideModal ? (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', display: 'grid', placeItems: 'center', padding: 16 }}>
          <div className="panel" style={{ width: 'min(460px, 100%)', padding: 20 }}>
            <h3 style={{ fontSize: 20, marginBottom: 12 }}>Override Zone - {overrideModal}</h3>
            <div className="form-grid">
              <div className="form-row">
                <label className="form-label">New Zone</label>
                <select className="form-input" value={overrideForm.zone} onChange={(e) => setOverrideForm((f) => ({ ...f, zone: parseInt(e.target.value, 10) }))}>
                  <option value={1}>Zone 1</option>
                  <option value={2}>Zone 2</option>
                  <option value={3}>Zone 3</option>
                  <option value={4}>Zone 4</option>
                  <option value={5}>Zone 5</option>
                </select>
              </div>
              <div className="form-row">
                <label className="form-label">Clinical Reason</label>
                <input className="form-input" value={overrideForm.reason} onChange={(e) => setOverrideForm((f) => ({ ...f, reason: e.target.value }))} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                <button className="btn-muted" onClick={() => setOverrideModal(null)}>Cancel</button>
                <button className="btn-black" onClick={submitOverride}>Confirm</button>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </ClinicalShell>
  );
}

function SimpleStat({ label, value }) {
  return (
    <div className="stat-pill">
      <div className="stat-pill-value">{value}</div>
      <div className="stat-pill-label">{label}</div>
    </div>
  );
}
