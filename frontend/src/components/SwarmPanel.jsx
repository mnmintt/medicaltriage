import { useState } from 'react';

export default function SwarmPanel({ triageResult }) {
  const [open, setOpen] = useState(false);
  if (!triageResult) return null;

  const agents = triageResult.agent_outputs || {};
  const entries = Object.entries(agents);
  const xgb = triageResult.xgboost_prediction;

  return (
    <div className="panel" style={{ padding: 16 }}>
      <button
        type="button"
        className="btn-muted"
        onClick={() => setOpen((v) => !v)}
        style={{ width: '100%', textAlign: 'left', display: 'flex', justifyContent: 'space-between' }}
      >
        <span>AI Swarm Reasoning</span>
        <span>{open ? 'Hide' : 'Show'}</span>
      </button>

      {open ? (
        <div style={{ marginTop: 12, display: 'grid', gap: 10 }}>
          {entries.length > 0 ? (
            entries.map(([key, value]) => (
              <div key={key} className="panel-soft" style={{ padding: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong style={{ textTransform: 'capitalize' }}>{key}</strong>
                  <span style={{ color: 'var(--text-soft)', fontSize: 12 }}>
                    {value.recommended_zone ? `Zone ${value.recommended_zone}` : value.final_zone ? `Zone ${value.final_zone}` : 'No zone'}
                  </span>
                </div>
                <div style={{ color: 'var(--text-body)', fontSize: 13, lineHeight: 1.5 }}>
                  {value.findings || value.clinical_narrative || 'No narrative provided.'}
                </div>
              </div>
            ))
          ) : (
            <div className="panel-soft" style={{ padding: 12, fontSize: 13, color: 'var(--text-soft)' }}>
              Swarm unavailable, showing fallback model output.
            </div>
          )}

          {xgb ? (
            <div className="panel-soft" style={{ padding: 12 }}>
              <strong style={{ display: 'block', marginBottom: 6 }}>XGBoost Fallback</strong>
              <div style={{ fontSize: 13, color: 'var(--text-body)' }}>
                Predicted Zone {xgb.zone} with {xgb.confidence}% confidence.
              </div>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
