import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import VitalsForm from '../components/VitalsForm';
import SymptomQuestionnaire from '../components/SymptomQuestionnaire';
import VisualFlagsForm from '../components/VisualFlagsForm';
import ClinicalShell from '../components/ClinicalShell';
import { submitTriage } from '../api';

const STEPS = ['Vitals', 'Symptoms', 'Visual AI', 'Review'];

const DEFAULT_VITALS = {
  systolic_bp: 120, diastolic_bp: 80, heart_rate: 75,
  spo2: 98, temperature: 36.8, respiratory_rate: 16,
};

const DEFAULT_SYMPTOMS = {
  pain_location: 'other', pain_severity: 0, onset_type: 'gradual',
  duration: '1-6hr', chest_crushing: false, chest_radiating: false,
  abdomen_vomiting: false, abdomen_fever: false, limb_deformity: false,
  limb_weight_bearing: true, loss_of_consciousness: false,
  difficulty_breathing: false, bleeding_severe: false,
};

const DEFAULT_VISUAL = {
  pallor: false, cyanosis: false, diaphoresis: false,
  gait_abnormality: false, facial_grimacing: false,
};

export default function KioskPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [vitals, setVitals] = useState({ ...DEFAULT_VITALS });
  const [symptoms, setSymptoms] = useState({ ...DEFAULT_SYMPTOMS });
  const [visualFlags, setVisualFlags] = useState({ ...DEFAULT_VISUAL });

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await submitTriage({ vitals, symptoms, visual_flags: visualFlags, language: 'en' });
      navigate(`/display/${result.id}`);
    } catch (err) {
      setError(err.message || 'Failed to submit triage');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ClinicalShell active="Kiosk" sideAction={<button className="btn-black" onClick={() => navigate('/') } style={{ width: '100%' }}>Back Home</button>}>
      <div className="canvas-narrow" style={{ display: 'grid', gap: 14 }}>
        <div className="panel" style={{ padding: 20 }}>
          <h2 style={{ fontSize: 26, marginBottom: 4 }}>Triage Intake</h2>
          <p style={{ color: 'var(--text-soft)', fontSize: 14 }}>Complete all sections before submission.</p>
          <div style={{ display: 'flex', gap: 8, marginTop: 14, flexWrap: 'wrap' }}>
            {STEPS.map((label, index) => (
              <button
                key={label}
                type="button"
                className={index === step ? 'btn-black' : 'btn-muted'}
                onClick={() => setStep(index)}
              >
                {index + 1}. {label}
              </button>
            ))}
          </div>
        </div>

        {step === 0 ? <VitalsForm values={vitals} onChange={(k, v) => setVitals((prev) => ({ ...prev, [k]: v }))} /> : null}
        {step === 1 ? <SymptomQuestionnaire values={symptoms} onChange={(k, v) => setSymptoms((prev) => ({ ...prev, [k]: v }))} /> : null}
        {step === 2 ? <VisualFlagsForm values={visualFlags} onChange={(k, v) => setVisualFlags((prev) => ({ ...prev, [k]: v }))} /> : null}
        {step === 3 ? <ReviewPanel vitals={vitals} symptoms={symptoms} visualFlags={visualFlags} /> : null}

        {error ? <div className="panel" style={{ padding: 14, color: 'var(--zone-1)' }}>{error}</div> : null}

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <button className="btn-muted" onClick={() => setStep((s) => Math.max(0, s - 1))}>Previous</button>
          {step < STEPS.length - 1 ? (
            <button className="btn-black" onClick={() => setStep((s) => s + 1)}>Next</button>
          ) : (
            <button className="btn-black" onClick={handleSubmit} disabled={loading}>{loading ? 'Submitting...' : 'Submit for Triage'}</button>
          )}
        </div>
      </div>
    </ClinicalShell>
  );
}

function ReviewPanel({ vitals, symptoms, visualFlags }) {
  return (
    <div className="panel" style={{ padding: 20 }}>
      <h3 style={{ fontSize: 18, marginBottom: 10 }}>Review</h3>
      <div className="kv-grid" style={{ marginBottom: 12 }}>
        <div className="kv-card"><div className="kv-label">Blood Pressure</div><div className="kv-value">{vitals.systolic_bp}/{vitals.diastolic_bp}</div></div>
        <div className="kv-card"><div className="kv-label">Heart Rate</div><div className="kv-value">{vitals.heart_rate}</div></div>
        <div className="kv-card"><div className="kv-label">SpO2</div><div className="kv-value">{vitals.spo2}%</div></div>
      </div>
      <div className="panel-soft" style={{ padding: 12, marginBottom: 10 }}>
        <div className="kv-label">Symptoms</div>
        <div style={{ color: 'var(--text-body)', fontSize: 14, lineHeight: 1.6 }}>
          Location: {symptoms.pain_location}, Severity: {symptoms.pain_severity}/10, Onset: {symptoms.onset_type}, Duration: {symptoms.duration}
        </div>
      </div>
      <div className="panel-soft" style={{ padding: 12 }}>
        <div className="kv-label">Visual Flags</div>
        <div style={{ color: 'var(--text-body)', fontSize: 14 }}>
          {Object.entries(visualFlags).filter(([, value]) => value).map(([key]) => key.replace('_', ' ')).join(', ') || 'None active'}
        </div>
      </div>
    </div>
  );
}
