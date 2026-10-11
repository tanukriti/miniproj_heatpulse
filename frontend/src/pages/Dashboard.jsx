import { useEffect, useState } from 'react';
import { BarChart3, MapPinned, MessageSquareText, ShieldAlert, TrendingUp, RefreshCcw } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { fetchJson } from '../services/api';

const COLORS = ['#f97316', '#f59e0b', '#10b981', '#f87171'];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [social, setSocial] = useState(null);
  const [weather, setWeather] = useState(null);
  const [gap, setGap] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [weatherData, socialData, gapData] = await Promise.all([
          fetchJson('/weather/summary'),
          fetchJson('/social/summary'),
          fetchJson('/gap-analysis'),
        ]);
        setWeather(weatherData);
        setSocial(socialData);
        setGap(gapData.items || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const sentimentData = Object.entries(social?.sentiment_distribution || {}).map(([name, value]) => ({ name, value }));
  const priorityData = (gap || []).slice(0, 5).map(item => ({ name: item.district, priority: Number(item.priority_score || 0) }));

  if (loading) return <div className="page-panel">Loading dashboard metrics…</div>;

  return (
    <div className="space-y-6">
      <div className="section-header">
        <div>
          <p className="eyebrow">Overview</p>
          <h1>Dashboard</h1>
        </div>
        <button className="ghost-button" type="button"><RefreshCcw size={16} /> Refresh data</button>
      </div>

      <div className="stats-grid">
        <StatCard icon={<BarChart3 />} label="Weather observations" value={weather?.observations || 0} detail="Current heat-risk sample" />
        <StatCard icon={<MapPinned />} label="Supported districts" value={weather?.district_count || 0} detail="Rajasthan coverage" />
        <StatCard icon={<MessageSquareText />} label="Social records" value={social?.total_posts || 0} detail="Demo listening sample" />
        <StatCard icon={<ShieldAlert />} label="Priority alerts" value={gap?.length || 0} detail="Risk–awareness–action findings" />
      </div>

      <div className="card-grid two-col">
        <div className="panel">
          <div className="panel-header">
            <h2>Sentiment distribution</h2>
            <TrendingUp size={18} />
          </div>
          <div className="chart-wrap soft">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={sentimentData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={75}>
                  {sentimentData.map((_, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2>Priority alerts</h2>
            <TrendingUp size={18} />
          </div>
          <div className="chart-wrap soft">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={priorityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="priority" fill="#f97316" radius={[6,6,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Recent communication priorities</h2>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>District</th>
                <th>Heat risk</th>
                <th>Engagement</th>
                <th>Priority</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {(gap || []).slice(0, 5).map(item => (
                <tr key={item.id || item.district}>
                  <td>{item.district}</td>
                  <td>{item.risk_score ?? '—'}</td>
                  <td>{item.engagement_score ?? '—'}</td>
                  <td>{Number(item.priority_score || 0).toFixed(2)}</td>
                  <td>{item.confidence || 'low'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, detail }) {
  return (
    <div className="stat-card">
      <div className="icon-box">{icon}</div>
      <div>
        <p className="stat-label">{label}</p>
        <h3>{value}</h3>
        <small>{detail}</small>
      </div>
    </div>
  );
}
