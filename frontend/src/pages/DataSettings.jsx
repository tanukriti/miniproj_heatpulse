import { useEffect, useState } from 'react';
import { fetchJson } from '../services/api';

export default function DataSettings() {
  const [datasets, setDatasets] = useState([]);

  useEffect(() => {
    fetchJson('/datasets').then(data => setDatasets(data.items || [])).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="section-header">
        <div>
          <p className="eyebrow">Settings</p>
          <h1>Data & Settings</h1>
        </div>
      </div>

      <div className="panel">
        <ul className="info-list">
          {datasets.map(dataset => (
            <li key={dataset.id}>
              <strong>{dataset.name}</strong>
              <span>{dataset.kind}</span>
              <span>{dataset.source}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
