export default function ExplanationCard({ explanation, zone }) {
  return (
    <div className="panel panel-explain">
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <strong style={{ fontFamily: 'Public Sans, sans-serif', fontSize: 14, color: 'var(--accent-blue)', letterSpacing: '0.08em' }}>
          WHY AM I WAITING?
        </strong>
      </div>
      <p style={{ whiteSpace: 'pre-line', lineHeight: 1.65, color: 'var(--text-body)', fontSize: 15 }}>
        {explanation}
      </p>
      <div style={{ borderTop: '1px solid var(--border-soft)', marginTop: 18, paddingTop: 12, color: 'var(--text-soft)', fontSize: 12 }}>
        Zone {zone} guidance updates automatically every 10 seconds.
      </div>
    </div>
  );
}
