import { useLocation, useNavigate } from 'react-router-dom';

const LINKS = [
  { label: 'Kiosk', to: '/kiosk' },
  { label: 'Dashboard', to: '/nurse' },
];

const SIDE_LINKS = [
  { key: 'live', label: 'Live Triage', to: '/kiosk' },
  { key: 'records', label: 'Patient Records', to: '/nurse?tab=records' },
];

function getActiveSideKey(pathname, search) {
  if (pathname.startsWith('/kiosk')) return 'live';
  if (pathname.startsWith('/display')) return 'records';
  if (pathname.startsWith('/nurse')) {
    const tab = new URLSearchParams(search).get('tab');
    return tab || 'records';
  }
  return 'records';
}

export default function ClinicalShell({ active = 'Kiosk', children, sideAction, compact = false }) {
  const navigate = useNavigate();
  const location = useLocation();
  const activeSideKey = getActiveSideKey(location.pathname, location.search);

  return (
    <div className="app-shell">
      <header className="top-nav">
        <div className="top-nav-left">
          <h1 className="brand-title">AI-Medical Triage</h1>
          <nav className="top-links">
            {LINKS.map((link) => {
              const isActive = link.label === active;
              return (
                <button
                  type="button"
                  key={link.label}
                  onClick={() => navigate(link.to)}
                  className={isActive ? 'top-link active' : 'top-link'}
                >
                  {link.label}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      <div className="shell-body">
        <aside className={compact ? 'side-nav compact' : 'side-nav'}>
          <div className="station-header">
            <div className="station-icon">M</div>
            <div>
              <div className="station-title">Nurse Station Alpha</div>
              <div className="station-subtitle">PRECISION ARCHIVE V1.0</div>
            </div>
          </div>

          <div className="side-links">
            {SIDE_LINKS.map((item) => (
              <button
                type="button"
                key={item.label}
                onClick={() => navigate(item.to)}
                className={item.key === activeSideKey ? 'side-link active' : 'side-link'}
              >
                {item.label}
              </button>
            ))}
          </div>

          {sideAction ? <div className="side-action">{sideAction}</div> : null}
        </aside>

        <main className="content-canvas">{children}</main>
      </div>
    </div>
  );
}
