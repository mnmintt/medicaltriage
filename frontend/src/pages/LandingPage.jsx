import { useNavigate } from 'react-router-dom';
import ClinicalShell from '../components/ClinicalShell';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <ClinicalShell active="Kiosk" sideAction={<button className="btn-black" onClick={() => navigate('/kiosk')} style={{ width: '100%' }}>New Intake</button>}>
      <div className="canvas-wide" style={{ display: 'grid', gap: 20 }}>
        <div className="panel" style={{ padding: 28 }}>
          <h2 style={{ fontSize: 34, marginBottom: 8 }}>AI-Medical Triage Platform</h2>
          <p style={{ fontSize: 16, color: 'var(--text-body)', maxWidth: 760, lineHeight: 1.7 }}>
            Precision intake for Malaysian emergency departments with guided triage, explainable patient communication,
            and nurse-facing decision support.
          </p>
        </div>

        <div className="stat-grid">
          <ActionCard title="Patient Kiosk" desc="Capture vitals, symptoms, and visual flags." action="Start" onClick={() => navigate('/kiosk')} />
          <ActionCard title="Nurse Dashboard" desc="Live patient queue with override controls." action="Launch" onClick={() => navigate('/nurse')} />
        </div>

        <div className="panel" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 20, marginBottom: 10 }}>Clinical Notes</h3>
          <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-body)', lineHeight: 1.8 }}>
            <li>Zone assignment follows 5-level triage logic.</li>
            <li>Swarm trace is available for nurse transparency.</li>
            <li>This prototype is decision support and not a replacement for clinical judgement.</li>
          </ul>
        </div>
      </div>
    </ClinicalShell>
  );
}

function ActionCard({ title, desc, action, onClick }) {
  return (
    <div className="panel" style={{ padding: 18 }}>
      <h3 style={{ fontSize: 18, marginBottom: 8 }}>{title}</h3>
      <p style={{ color: 'var(--text-soft)', fontSize: 14, minHeight: 42 }}>{desc}</p>
      <button className="btn-black" style={{ marginTop: 14 }} onClick={onClick}>{action}</button>
    </div>
  );
}
