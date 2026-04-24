export default function BodyMap({ selected, onSelect }) {
  const areas = ['head', 'chest', 'abdomen', 'limb', 'back', 'other'];

  return (
    <div className="panel" style={{ padding: 20 }}>
      <div style={{ marginBottom: 14 }}>
        <h3 style={{ fontSize: 18, marginBottom: 4 }}>Pain Location</h3>
        <p style={{ color: 'var(--text-soft)', fontSize: 14 }}>Select the area that hurts most.</p>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
        {areas.map((area) => {
          const active = selected === area;
          return (
            <button
              key={area}
              type="button"
              onClick={() => onSelect(area)}
              className={active ? 'btn-black' : 'btn-muted'}
              style={{ textTransform: 'capitalize', minWidth: 110 }}
            >
              {area}
            </button>
          );
        })}
      </div>
    </div>
  );
}
