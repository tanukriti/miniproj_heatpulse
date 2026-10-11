import { render, screen } from '@testing-library/react';
import App from './App';

test('renders dashboard navigation and HeatPulse title', () => {
  window.history.pushState({}, '', '/dashboard');

  render(<App />);

  expect(screen.getAllByText('HeatPulse').length).toBeGreaterThan(0);
  expect(screen.getByText('Dashboard')).toBeInTheDocument();
});
