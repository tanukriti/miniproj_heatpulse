import { useEffect, useState } from 'react';
import { fetchJson } from '../services/api';

export default function GapDetector() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchJson('/gap-analysis');
        setItems(data.items || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className="page-panel">Loading gap analysis…</div>;

  return (
    <div className="space-y-6">
      <div className="section-header">
        <div>
          <p className="eyebrow">Research engine</p>
          <h1>Risk–Awareness–Action Gap Detector</h1>
        </div>
      </div>

      <div className="panel">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>District</th>
                <th>Risk</th>
                <th>Engagement</th>
                <th>Priority</th>
                <th>Evidence</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id || item.district}>
                  <td>{item.district}</td>
                  <td>{item.risk_score}</td>
                  <td>{item.engagement_score}</td>
                  <td>{Number(item.priority_score || 0).toFixed(2)}</td>
                  <td>{item.evidence_count}</td>
                  <td>{item.confidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
