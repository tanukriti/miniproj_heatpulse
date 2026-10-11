import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom';
import { Activity, BarChart3, CalendarDays, Flame, LayoutDashboard, Map, MessageSquareText, Settings, Sparkles, TrendingUp } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import HeatwaveMap from './pages/HeatwaveMap';
import SocialListening from './pages/SocialListening';
import GapDetector from './pages/GapDetector';
import CampaignStudio from './pages/CampaignStudio';
import ContentCalendar from './pages/ContentCalendar';
import CampaignAnalytics from './pages/CampaignAnalytics';
import ModelPerformance from './pages/ModelPerformance';
import DataSettings from './pages/DataSettings';

const navItems = [
  { title: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { title: 'Heatwave Intelligence', path: '/heatwave-map', icon: Map },
  { title: 'Social Listening', path: '/social-listening', icon: MessageSquareText },
  { title: 'Gap Detector', path: '/gap-detector', icon: Flame },
  { title: 'Campaign Studio', path: '/campaign-studio', icon: Sparkles },
  { title: 'Content Calendar', path: '/content-calendar', icon: CalendarDays },
  { title: 'Campaign Analytics', path: '/campaign-analytics', icon: BarChart3 },
  { title: 'Model Performance', path: '/model-performance', icon: TrendingUp },
  { title: 'Data & Settings', path: '/data-settings', icon: Settings },
];

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand-row">
            <div className="brand-mark"><Activity size={18} /></div>
            <div>
              <strong>HeatPulse</strong>
              <small>Risk intelligence</small>
            </div>
          </div>
          <nav className="nav-stack">
            {navItems.map(({ title, path, icon: Icon }) => (
              <NavLink key={path} to={path} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <Icon size={16} />
                <span>{title}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="content-area">
          <header className="topbar">
            <div>
              <p className="eyebrow">Academic demo</p>
              <h1>HeatPulse</h1>
            </div>
          </header>

          <div className="page-shell">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/heatwave-map" element={<HeatwaveMap />} />
              <Route path="/social-listening" element={<SocialListening />} />
              <Route path="/gap-detector" element={<GapDetector />} />
              <Route path="/campaign-studio" element={<CampaignStudio />} />
              <Route path="/content-calendar" element={<ContentCalendar />} />
              <Route path="/campaign-analytics" element={<CampaignAnalytics />} />
              <Route path="/model-performance" element={<ModelPerformance />} />
              <Route path="/data-settings" element={<DataSettings />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
