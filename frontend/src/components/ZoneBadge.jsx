const ZONE_NAMES = {
  1: 'Zone 1',
  2: 'Zone 2',
  3: 'Zone 3',
  4: 'Zone 4',
  5: 'Zone 5',
};

const ZONE_COLOURS = {
  1: 'Red',
  2: 'Orange',
  3: 'Yellow',
  4: 'Green',
  5: 'Blue',
};

const ZONE_COLOR_VALUES = {
  1: 'var(--zone-1)',
  2: 'var(--zone-2)',
  3: 'var(--zone-3)',
  4: 'var(--zone-4)',
  5: 'var(--zone-5)',
};

export default function ZoneBadge({ zone, size = 'md', showLabel = false }) {
  const padding = size === 'sm' ? '3px 8px' : size === 'lg' ? '6px 14px' : '4px 10px';
  const fontSize = size === 'sm' ? 11 : size === 'lg' ? 14 : 12;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span
        className="zone-chip"
        style={{
          background: ZONE_COLOR_VALUES[zone] || 'var(--zone-4)',
          padding,
          fontSize,
        }}
      >
        {ZONE_NAMES[zone]} - {ZONE_COLOURS[zone]}
      </span>
      {showLabel ? <span style={{ color: 'var(--text-soft)', fontSize: 13 }}>Clinical priority indicator</span> : null}
    </div>
  );
}
