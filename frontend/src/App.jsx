import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import KioskPage from './pages/KioskPage';
import PatientDisplayPage from './pages/PatientDisplayPage';
import NurseDashboardPage from './pages/NurseDashboardPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/kiosk" element={<KioskPage />} />
        <Route path="/display/:id" element={<PatientDisplayPage />} />
        <Route path="/nurse" element={<NurseDashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
