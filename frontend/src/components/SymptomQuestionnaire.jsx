import BodyMap from './BodyMap';

const CHEST_QUESTIONS = [
  { key: 'chest_crushing', label: 'Crushing or pressure-like chest pain?' },
  { key: 'chest_radiating', label: 'Pain radiating to arm or jaw?' },
];

const ABDOMEN_QUESTIONS = [
  { key: 'abdomen_vomiting', label: 'Associated vomiting?' },
  { key: 'abdomen_fever', label: 'Associated fever?' },
];

const LIMB_QUESTIONS = [
  { key: 'limb_deformity', label: 'Visible deformity?' },
  { key: 'limb_weight_bearing', label: 'Can bear weight?' },
];

const GENERAL_QUESTIONS = [
  { key: 'loss_of_consciousness', label: 'Loss of consciousness?' },
  { key: 'difficulty_breathing', label: 'Difficulty breathing?' },
  { key: 'bleeding_severe', label: 'Severe bleeding?' },
];

const ONSET_OPTIONS = ['sudden', 'gradual'];
const DURATION_OPTIONS = ['<1hr', '1-6hr', '6-24hr', '>24hr'];

export default function SymptomQuestionnaire({ values, onChange }) {
  const location = values.pain_location || '';

  const branchQuestions =
    location === 'chest'
      ? CHEST_QUESTIONS
      : location === 'abdomen'
      ? ABDOMEN_QUESTIONS
      : location === 'limb'
      ? LIMB_QUESTIONS
      : [];

  return (
    <div style={{ display: 'grid', gap: 14 }}>
      <BodyMap selected={location} onSelect={(area) => onChange('pain_location', area)} />

      <div className="panel" style={{ padding: 20 }}>
        <div className="form-grid">
          <div className="form-row">
            <label className="form-label">Pain Severity ({values.pain_severity ?? 0}/10)</label>
            <input
              type="range"
              className="range-slider"
              min={0}
              max={10}
              step={1}
              value={values.pain_severity ?? 0}
              onChange={(e) => onChange('pain_severity', parseInt(e.target.value, 10))}
            />
          </div>

          <div className="form-row">
            <label className="form-label">Onset Type</label>
            <div style={{ display: 'flex', gap: 8 }}>
              {ONSET_OPTIONS.map((opt) => (
                <button
                  key={opt}
                  type="button"
                  className={values.onset_type === opt ? 'btn-black' : 'btn-muted'}
                  onClick={() => onChange('onset_type', opt)}
                >
                  {opt}
                </button>
              ))}
            </div>
          </div>

          <div className="form-row">
            <label className="form-label">Duration</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {DURATION_OPTIONS.map((opt) => (
                <button
                  key={opt}
                  type="button"
                  className={values.duration === opt ? 'btn-black' : 'btn-muted'}
                  onClick={() => onChange('duration', opt)}
                >
                  {opt}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {branchQuestions.length > 0 ? (
        <QuestionBlock title="Location-specific Questions" questions={branchQuestions} values={values} onChange={onChange} />
      ) : null}

      <QuestionBlock title="General Symptoms" questions={GENERAL_QUESTIONS} values={values} onChange={onChange} />
    </div>
  );
}

function QuestionBlock({ title, questions, values, onChange }) {
  return (
    <div className="panel" style={{ padding: 20 }}>
      <label className="form-label" style={{ marginBottom: 10, display: 'block' }}>{title}</label>
      <div style={{ display: 'grid', gap: 10 }}>
        {questions.map((q) => (
          <div key={q.key} className="panel-soft" style={{ padding: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 14, color: 'var(--text-body)' }}>{q.label}</span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button type="button" className={values[q.key] === true ? 'btn-black' : 'btn-muted'} onClick={() => onChange(q.key, true)}>Yes</button>
              <button type="button" className={values[q.key] === false ? 'btn-black' : 'btn-muted'} onClick={() => onChange(q.key, false)}>No</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
