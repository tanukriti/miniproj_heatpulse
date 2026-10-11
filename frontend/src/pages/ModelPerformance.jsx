import { useEffect, useState } from 'react';
import { fetchJson } from '../services/api';

export default function ModelPerformance() {
  const [models, setModels] = useState([]);

  useEffect(() => {
    fetchJson('/models/evaluation').then(data => setModels(data.items || [])).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="section-header">
        <div>
          <p className="eyebrow">Model review</p>
          <h1>Model Performance</h1>
        </div>
      </div>

      <div className="panel">
        <ul className="info-list">
          {models.map(model => (
            <li key={`${model.model_name}-${model.metric_name}`}>
              <strong>{model.model_name}</strong>
              <span>{model.metric_name}</span>
              <span>{Number(model.value).toFixed(2)}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
