from backend.app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get('/api/health')
    assert response.status_code == 200
    body = response.get_json()
    assert body['status'] == 'ok'


def test_weather_summary_endpoint():
    client = app.test_client()
    response = client.get('/api/weather/summary')
    assert response.status_code == 200
    body = response.get_json()
    assert body['observations'] > 0
    assert body['district_count'] > 0


def test_social_post_filtering():
    client = app.test_client()
    response = client.get('/api/social/posts?district=Jaipur')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] >= 1


def test_gap_analysis_calculation():
    client = app.test_client()
    response = client.post('/api/gap-analysis/recalculate', json={'district': 'Jaipur', 'risk_score': 90, 'engagement_score': 20, 'evidence_count': 5})
    assert response.status_code == 200
    body = response.get_json()
    assert body['priority_score'] > 0
    assert body['priority_score'] < 1


def test_campaign_create_and_edit():
    client = app.test_client()
    create_response = client.post('/api/campaigns', json={'title': 'Test campaign', 'objective': 'Awareness', 'district': 'Jodhpur', 'topic': 'hydration', 'platform': 'Instagram'})
    assert create_response.status_code == 201
    created = create_response.get_json()
    update_response = client.patch(f"/api/campaigns/{created['id']}", json={'status': 'approved'})
    assert update_response.status_code == 200
    assert update_response.get_json()['status'] == 'approved'


def test_draft_scheduling_validation():
    client = app.test_client()
    draft = client.post('/api/drafts', json={'title': 'Draft', 'body': 'Test', 'status': 'draft', 'platform': 'Instagram'}).get_json()
    schedule_response = client.post('/api/schedules', json={'draft_id': draft['id'], 'scheduled_for': '2026-12-01T09:00:00'})
    assert schedule_response.status_code == 201


def test_csv_validation_and_invalid_request():
    client = app.test_client()
    bad = client.post('/api/data/validate', json={'date': '2026-06-01'})
    assert bad.status_code == 400
    good = client.post('/api/data/validate', json={'district': 'Jaipur', 'date': '2026-06-01', 'max_temp_c': 41.6})
    assert good.status_code == 200
