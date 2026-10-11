# HeatPulse

HeatPulse is a demonstration-grade public heatwave intelligence and campaign-planning system for Rajasthan. It combines weather-risk indicators, social-listening summaries, a Risk–Awareness–Action engine, campaign planning, and model-performance reporting in a single local application.

## Stack
- Frontend: React + Vite + React Router + Recharts + Tailwind CSS + Leaflet
- Backend: Flask + Flask-SQLAlchemy + SQLite
- ML: scikit-learn, rule-based classification, and reproducible synthetic demonstration data

## Run locally

### Backend
```powershell
cd "d:\TANU\OneDrive\Desktop\DV&SMA MINIPROJ"
.\.venv\Scripts\python.exe -m flask --app backend.app run --debug
```

### Frontend
```powershell
cd "d:\TANU\OneDrive\Desktop\DV&SMA MINIPROJ\frontend"
npm run dev -- --host 0.0.0.0
```

## Default URLs
- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:5000/api/health

## Demo mode
This project uses synthetic Rajasthan weather and social-media data when external services are unavailable. All derived charts and social posts are intentionally labelled as demonstration data and are not official public posts.

## Notes
- The app is designed for academic demo use and to run offline in local development without external API credentials.
- API keys and private credentials should remain server-side only.
