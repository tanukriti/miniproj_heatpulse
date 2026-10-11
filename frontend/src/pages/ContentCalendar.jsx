const events = [
  { id: 1, title: 'Jaipur hydration awareness', date: '2026-10-15', status: 'scheduled', platform: 'Instagram' },
  { id: 2, title: 'Jodhpur cooling access', date: '2026-10-18', status: 'approved', platform: 'WhatsApp' },
];

export default function ContentCalendar() {
  return (
    <div className="space-y-6">
      <div className="section-header">
        <div>
          <p className="eyebrow">Scheduling</p>
          <h1>Content Calendar</h1>
        </div>
      </div>

      <div className="panel">
        <div className="calendar-grid">
          {events.map(item => (
            <div key={item.id} className="calendar-card">
              <strong>{item.title}</strong>
              <span>{item.date}</span>
              <span>{item.platform}</span>
              <span className="tag">{item.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
