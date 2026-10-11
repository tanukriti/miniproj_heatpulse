import { useEffect, useState } from 'react';
import { fetchJson } from '../services/api';

export default function SocialListening() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [district, setDistrict] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const params = new URLSearchParams();
        if (query) params.set('q', query);
        if (district) params.set('district', district);
        const data = await fetchJson(`/social/posts?${params.toString()}`);
        setPosts(data.items || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [query, district]);

  return (
    <div className="space-y-6">
      <div className="section-header">
        <div>
          <p className="eyebrow">Community signals</p>
          <h1>Social Listening</h1>
        </div>
      </div>

      <div className="panel filter-panel">
        <input className="input-box" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search posts or keywords" />
        <select className="select-box" value={district} onChange={event => setDistrict(event.target.value)}>
          <option value="">All districts</option>
          <option value="Jaipur">Jaipur</option>
          <option value="Jodhpur">Jodhpur</option>
          <option value="Kota">Kota</option>
        </select>
      </div>

      <div className="panel">
        {loading ? (
          <p>Loading social posts…</p>
        ) : posts.length === 0 ? (
          <p>No matching posts found.</p>
        ) : (
          <div className="list-stack">
            {posts.map(post => (
              <article key={post.id} className="post-card">
                <div className="post-meta">
                  <span>{post.district || 'Unknown district'}</span>
                  <span>{post.topic}</span>
                  <span>{post.sentiment}</span>
                </div>
                <p>{post.text}</p>
                <small>Demo social record • {new Date(post.timestamp).toLocaleString()}</small>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
