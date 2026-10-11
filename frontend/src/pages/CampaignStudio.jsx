import { useState } from 'react';

export default function CampaignStudio() {
  const [draft, setDraft] = useState('')
  const [title, setTitle] = useState('Hydration awareness reminder')
  const [district, setDistrict] = useState('Jaipur')
  const [platform, setPlatform] = useState('Instagram')

  const handleGenerate = () => {
    setDraft(`🚨 ${district} के लिए गर्मी सुरक्षा: सुबह/शाम में बाहर निकलें, पानी पीते रहें, और छायादार स्थानों का उपयोग करें। अधिक जानकारी के लिए स्थानीय हेल्पलाइन/सुरक्षा सूचना देखें.`)
  }

  return (
    <div className="space-y-6">
      <div className="section-header">
        <div>
          <p className="eyebrow">Public communication</p>
          <h1>AI Campaign Studio</h1>
        </div>
      </div>

      <div className="card-grid two-col">
        <div className="panel">
          <label className="field">
            <span>Campaign title</span>
            <input className="input-box" value={title} onChange={event => setTitle(event.target.value)} />
          </label>
          <label className="field">
            <span>District</span>
            <select className="select-box" value={district} onChange={event => setDistrict(event.target.value)}>
              <option>Jaipur</option>
              <option>Jodhpur</option>
              <option>Kota</option>
            </select>
          </label>
          <label className="field">
            <span>Platform</span>
            <select className="select-box" value={platform} onChange={event => setPlatform(event.target.value)}>
              <option>Instagram</option>
              <option>WhatsApp</option>
              <option>Facebook</option>
            </select>
          </label>
          <button className="primary-button" type="button" onClick={handleGenerate}>Generate draft</button>
        </div>

        <div className="panel">
          <h2>Generated message</h2>
          <textarea className="textarea-box" value={draft} onChange={event => setDraft(event.target.value)} />
          <div className="inline-actions">
            <button className="primary-button" type="button">Save draft</button>
            <button className="ghost-button" type="button">Approve</button>
          </div>
        </div>
      </div>
    </div>
  )
}
