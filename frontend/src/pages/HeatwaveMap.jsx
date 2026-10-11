import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import { fetchJson } from '../services/api';

const districtPoints = {
  Jaipur: [26.9124, 75.7873],
  Jodhpur: [26.2389, 73.0243],
  Kota: [25.2138, 75.8648],
  Bikaner: [28.0229, 73.3119],
  Ajmer: [26.4499, 74.6371],
  Udaipur: [24.5854, 73.7125],
  Alwar: [27.5615, 76.6250],
};

export default function HeatwaveMap() {
  const [weather, setWeather] = useState([]);
  const [selectedDistrict, setSelectedDistrict] = useState('Jaipur');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchJson('/weather/risk');
        setWeather(data.items || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const selectedData = weather.filter(item => item.district === selectedDistrict).slice(0, 5);

  if (loading) return <div className="page-panel">Loading map data…</div>;

  return (
    <div className="space-y-6">
      <div className="section-header">
        <div>
          <p className="eyebrow">Weather intelligence</p>
          <h1>Heatwave Intelligence Map</h1>
        </div>
        <select value={selectedDistrict} onChange={event => setSelectedDistrict(event.target.value)} className="select-box">
          {Object.keys(districtPoints).map(name => <option key={name} value={name}>{name}</option>)}
        </select>
      </div>

      <div className="card-grid two-col">
        <div className="panel map-panel">
          <MapContainer center={[26.5, 74.5]} zoom={6} scrollWheelZoom className="map-container">
            <TileLayer
              attribution='&copy; OpenStreetMap contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {Object.entries(districtPoints).map(([district, position]) => {
              const districtRisk = (weather.find(item => item.district === district)?.risk_score) || 0;
              return (
                <CircleMarker
                  key={district}
                  center={position}
                  radius={Math.max(9, districtRisk / 7)}
                  pathOptions={{ color: riskColor(districtRisk), fillColor: riskColor(districtRisk), fillOpacity: 0.7 }}
                  eventHandlers={{ click: () => setSelectedDistrict(district) }}
                >
                  <Tooltip>{district}: {districtRisk.toFixed(1)} risk</Tooltip>
                  <Popup>{district}<br />Risk score: {districtRisk.toFixed(1)}</Popup>
                </CircleMarker>
              );
            })}
          </MapContainer>
        </div>

        <div className="panel">
          <div className="panel-header"><h2>{selectedDistrict} details</h2></div>
          <ul className="info-list">
            {selectedData.length ? selectedData.map(item => (
              <li key={item.id}>
                <strong>{item.date}</strong>
                <span>Risk {item.risk_score}</span>
                <span>Level {item.risk_level}</span>
              </li>
            )) : <li>No recent records for this district.</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}

function riskColor(score) {
  if (score >= 75) return '#dc2626';
  if (score >= 55) return '#f97316';
  if (score >= 35) return '#f59e0b';
  return '#22c55e';
}
