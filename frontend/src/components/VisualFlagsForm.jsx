const FLAGS = [
  { key: 'pallor', label: 'Pallor', desc: 'Skin pallor detected' },
  { key: 'cyanosis', label: 'Cyanosis', desc: 'Bluish discolouration detected' },
  { key: 'diaphoresis', label: 'Diaphoresis', desc: 'Visible diaphoresis detected' },
  { key: 'gait_abnormality', label: 'Gait Abnormality', desc: 'Abnormal gait pattern detected' },
  { key: 'facial_grimacing', label: 'Facial Grimacing', desc: 'Pain expression detected' },
];

export default function VisualFlagsForm({ values, onChange }) {
  return (
    <div className="panel" style={{ padding: 20 }}>
      <h3 style={{ fontSize: 18, marginBottom: 4 }}>Visual AI Flags</h3>
      <p style={{ color: 'var(--text-soft)', fontSize: 14, marginBottom: 14 }}>Toggle simulated camera findings.</p>

      <div style={{ display: 'grid', gap: 10 }}>
        {FLAGS.map((flag) => (
          <div key={flag.key} className="panel-soft" style={{ padding: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontFamily: 'Public Sans, sans-serif', fontWeight: 700, fontSize: 14 }}>{flag.label}</div>
              <div style={{ fontSize: 12, color: 'var(--text-soft)' }}>{flag.desc}</div>
            </div>
            <label className="toggle-switch">
              <input type="checkbox" checked={values[flag.key] || false} onChange={(e) => onChange(flag.key, e.target.checked)} />
              <span className="toggle-slider" />
            </label>
          </div>
        ))}
      </div>
    </div>
  );
}
