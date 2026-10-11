import { useEffect, useState } from 'react';
import { fetchJson } from '../services/api';

export default function CampaignAnalytics() {
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    fetchJson('/campaign-metrics').then(data => setMetrics(data.items || [])).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="section-header">
        <div>
          <p className="eyebrow">Performance</p>
          <h1>Campaign Analytics</h1>
        </div>
      </div>

      <div className="panel">
        <table>
          <thead>
            <tr>
              <th>Campaign</th>
              <th>Reach</th>
              <th>Impressions</th>
              <th>Engagement</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map(item => (
              <tr key={item.id}>
                <td>{item.campaign_id}</td>
                <td>{item.reach}</td>
                <td>{item.impressions}</td>
                <td>{item.engagement_rate}</td>
                <td>{item.source_type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
