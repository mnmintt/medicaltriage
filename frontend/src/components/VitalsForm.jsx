const VITAL_CONFIGS = [
  { key: 'systolic_bp', label: 'Systolic BP', unit: 'mmHg', min: 40, max: 260, step: 1, default: 120 },
  { key: 'diastolic_bp', label: 'Diastolic BP', unit: 'mmHg', min: 20, max: 160, step: 1, default: 80 },
  { key: 'heart_rate', label: 'Heart Rate', unit: 'bpm', min: 20, max: 220, step: 1, default: 75 },
  { key: 'spo2', label: 'SpO2', unit: '%', min: 50, max: 100, step: 0.5, default: 98 },
  { key: 'temperature', label: 'Temperature', unit: 'C', min: 30, max: 43, step: 0.1, default: 36.8 },
  { key: 'respiratory_rate', label: 'Respiratory Rate', unit: 'br/min', min: 4, max: 60, step: 1, default: 16 },
];

export default function VitalsForm({ values, onChange }) {
  return (
    <div className="panel" style={{ padding: 20 }}>
      <h3 style={{ fontSize: 18, marginBottom: 4 }}>Vital Signs</h3>
      <p style={{ color: 'var(--text-soft)', fontSize: 14, marginBottom: 16 }}>Set observed values from triage intake.</p>

      <div style={{ display: 'grid', gap: 12 }}>
        {VITAL_CONFIGS.map((config) => {
          const value = values[config.key] ?? config.default;
          return (
            <div key={config.key} className="panel-soft" style={{ padding: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <label style={{ fontFamily: 'Public Sans, sans-serif', fontSize: 13, fontWeight: 700 }}>{config.label}</label>
                <span style={{ fontFamily: 'IBM Plex Mono, monospace' }}>
                  {typeof value === 'number' ? value : config.default} {config.unit}
                </span>
              </div>
              <input
                type="range"
                className="range-slider"
                min={config.min}
                max={config.max}
                step={config.step}
                value={value}
                onChange={(e) => onChange(config.key, parseFloat(e.target.value))}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}

export { VITAL_CONFIGS };
