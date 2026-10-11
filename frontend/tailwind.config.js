/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: '#0f172a',
        heat: '#f97316',
        heatDark: '#c2410c',
        danger: '#dc2626',
        warning: '#f59e0b',
        success: '#10b981',
        slate: '#e2e8f0'
      },
      boxShadow: {
        soft: '0 10px 30px rgba(15,23,42,0.08)'
      }
    }
  },
  plugins: []
}