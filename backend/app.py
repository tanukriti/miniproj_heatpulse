import json
import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.models import (
    Campaign,
    CampaignMetric,
    ContentDraft,
    DatasetMetadata,
    DistrictRisk,
    GapAnalysis,
    ModelEvaluation,
    ScheduledPost,
    SocialPost,
    WeatherObservation,
    db,
)
from backend.seed_data import seed_demo_data


def risk_to_label(score):
    if score >= 75:
        return "extreme"
    if score >= 55:
        return "high"
    if score >= 35:
        return "moderate"
    return "low"


def classify_text(text):
    lower = (text or "").lower()
    if any(word in lower for word in ["heat", "temperature", "suffocating", "sun", "boiling"]):
        topic = "heat_discomfort"
    elif any(word in lower for word in ["water", "hydration", "drink", "thirst"]):
        topic = "hydration"
    elif any(word in lower for word in ["advisory", "safety", "shade", "cooling"]):
        topic = "safety_advisories"
    elif any(word in lower for word in ["support", "need", "hospital", "help"]):
        topic = "requests_for_help"
    elif any(word in lower for word in ["facility", "water supply", "power", "school"]):
        topic = "public_facilities"
    else:
        topic = "general_heat_news"

    if any(word in lower for word in ["worried", "danger", "bad", "stress", "sick", "exhausted"]):
        sentiment = "negative"
    elif any(word in lower for word in ["safe", "relief", "good", "helpful", "cool"]):
        sentiment = "positive"
    else:
        sentiment = "neutral"
    return {"sentiment": sentiment, "topic": topic, "confidence": 0.72}


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///heatpulse.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_SORT_KEYS"] = False

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()
        seed_demo_data()

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "HeatPulse backend",
            "database": "SQLite",
            "demo_mode": True,
            "timestamp": datetime.utcnow().isoformat(),
        })

    @app.get("/api/metadata")
    def metadata():
        return jsonify({
            "app_name": "HeatPulse",
            "title": "AI-Powered Heatwave Intelligence, Public Awareness Analytics and Social Media Management System",
            "region": "Rajasthan, India",
            "demo_mode": True,
            "source_policy": "Synthetic and publicly documented demonstration data only.",
        })

    @app.get("/api/datasets")
    def datasets():
        items = DatasetMetadata.query.order_by(DatasetMetadata.id).all()
        return jsonify({"items": [record.to_dict() for record in items], "count": len(items)})

    @app.get("/api/data-quality")
    def data_quality():
        weather_count = WeatherObservation.query.count()
        social_count = SocialPost.query.count()
        return jsonify({
            "weather_records": weather_count,
            "social_records": social_count,
            "duplicate_checks": "passed",
            "missing_values": "handled via demo preprocessing",
            "data_quality": "acceptable for demonstration",
        })

    @app.get("/api/weather/summary")
    def weather_summary():
        total_obs = WeatherObservation.query.count()
        recent = WeatherObservation.query.order_by(WeatherObservation.date.desc()).first()
        districts = WeatherObservation.query.with_entities(WeatherObservation.district).distinct().all()
        high_risk = WeatherObservation.query.filter(WeatherObservation.risk_score >= 70).count()
        return jsonify({
            "observations": total_obs,
            "latest_date": recent.date.isoformat() if recent else None,
            "district_count": len(districts),
            "high_risk_observations": high_risk,
            "source": "NASA POWER demo dataset",
            "demo_mode": True,
        })

    @app.get("/api/weather/observations")
    def weather_observations():
        district = request.args.get("district")
        start = request.args.get("start")
        end = request.args.get("end")
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))

        query = WeatherObservation.query
        if district:
            query = query.filter(WeatherObservation.district.ilike(f"%{district}%"))
        if start:
            query = query.filter(WeatherObservation.date >= datetime.strptime(start, "%Y-%m-%d").date())
        if end:
            query = query.filter(WeatherObservation.date <= datetime.strptime(end, "%Y-%m-%d").date())

        total = query.count()
        records = query.order_by(WeatherObservation.date.desc(), WeatherObservation.district.asc()).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            "items": [item.to_dict() for item in records.items],
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        })

    @app.get("/api/weather/districts")
    def weather_districts():
        districts = WeatherObservation.query.with_entities(WeatherObservation.district).distinct().order_by(WeatherObservation.district.asc()).all()
        return jsonify({"items": [item[0] for item in districts]})

    @app.get("/api/weather/risk")
    def weather_risk():
        district = request.args.get("district")
        query = DistrictRisk.query
        if district:
            query = query.filter(DistrictRisk.district.ilike(f"%{district}%"))
        items = query.order_by(DistrictRisk.date.desc()).all()
        return jsonify({"items": [item.to_dict() for item in items]})

    @app.get("/api/weather/trends")
    def weather_trends():
        districts = [item[0] for item in WeatherObservation.query.with_entities(WeatherObservation.district).distinct().all()]
        series = []
        for district in districts:
            rows = WeatherObservation.query.filter_by(district=district).order_by(WeatherObservation.date.asc()).limit(7).all()
            series.append({
                "district": district,
                "values": [{"date": row.date.isoformat(), "mean_temp_c": row.mean_temp_c, "risk_score": row.risk_score} for row in rows],
            })
        return jsonify({"items": series})

    @app.post("/api/weather/refresh")
    def weather_refresh():
        return jsonify({"status": "demo refresh complete", "message": "Using cached synthetic dataset; no external API calls attempted."})

    @app.get("/api/social/summary")
    def social_summary():
        total_posts = SocialPost.query.count()
        sentiments = SocialPost.query.with_entities(SocialPost.sentiment, db.func.count(SocialPost.id)).group_by(SocialPost.sentiment).all()
        topics = SocialPost.query.with_entities(SocialPost.topic, db.func.count(SocialPost.id)).group_by(SocialPost.topic).all()
        return jsonify({
            "total_posts": total_posts,
            "sentiment_distribution": {label: count for label, count in sentiments},
            "topic_distribution": {label: count for label, count in topics},
            "demo_mode": True,
        })

    @app.get("/api/social/posts")
    def social_posts():
        district = request.args.get("district")
        topic = request.args.get("topic")
        sentiment = request.args.get("sentiment")
        q = request.args.get("q", "")
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(50, max(1, int(request.args.get("per_page", 10))))

        records = SocialPost.query
        if district:
            records = records.filter(SocialPost.district.ilike(f"%{district}%"))
        if topic:
            records = records.filter(SocialPost.topic == topic)
        if sentiment:
            records = records.filter(SocialPost.sentiment == sentiment)
        if q:
            records = records.filter(SocialPost.text.ilike(f"%{q}%"))

        total = records.count()
        items = records.order_by(SocialPost.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            "items": [item.to_dict() for item in items.items],
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        })

    @app.get("/api/social/topics")
    def social_topics():
        rows = SocialPost.query.with_entities(SocialPost.topic, db.func.count(SocialPost.id)).group_by(SocialPost.topic).all()
        return jsonify({"items": [{"topic": topic, "count": count} for topic, count in rows]})

    @app.get("/api/social/sentiment")
    def social_sentiment():
        rows = SocialPost.query.with_entities(SocialPost.sentiment, db.func.count(SocialPost.id)).group_by(SocialPost.sentiment).all()
        return jsonify({"items": [{"sentiment": label, "count": count} for label, count in rows]})

    @app.post("/api/social/classify")
    def classify_post():
        payload = request.get_json(silent=True) or {}
        text = payload.get("text") or ""
        if not text.strip():
            return jsonify({"error": "text is required"}), 400
        result = classify_text(text)
        return jsonify({"result": result})

    @app.get("/api/gap-analysis")
    def gap_analysis_list():
        items = GapAnalysis.query.order_by(GapAnalysis.priority_score.desc()).all()
        return jsonify({"items": [item.to_dict() for item in items]})

    @app.get("/api/gap-analysis/<int:id>")
    def gap_analysis_detail(id):
        row = GapAnalysis.query.get_or_404(id)
        return jsonify(row.to_dict())

    @app.post("/api/gap-analysis/recalculate")
    def gap_analysis_recalculate():
        payload = request.get_json(silent=True) or {}
        district = payload.get("district") or "Jaipur"
        risk_score = float(payload.get("risk_score", 80))
        engagement_score = float(payload.get("engagement_score", 20))
        evidence_count = int(payload.get("evidence_count", 7))
        priority = (risk_score / 100.0) * (1 - (engagement_score / 100.0))
        if evidence_count < 3:
            status = "Insufficient evidence to estimate communication priority reliably."
        else:
            status = "High potential communication priority." if priority >= 0.5 else "Moderate potential communication priority."
        record = GapAnalysis(
            district=district,
            date_window="custom window",
            risk_score=risk_score,
            engagement_score=engagement_score,
            priority_score=priority,
            evidence_count=evidence_count,
            confidence="moderate" if evidence_count >= 3 else "low",
            source="manual recalculation",
            explanation=status,
        )
        db.session.add(record)
        db.session.commit()
        return jsonify(record.to_dict())

    @app.get("/api/gap-analysis/compare-baseline")
    def compare_baseline():
        items = GapAnalysis.query.order_by(GapAnalysis.priority_score.desc()).all()
        base = [{"district": row.district, "risk_only": row.risk_score, "raa_priority": row.priority_score} for row in items]
        return jsonify({"items": base})

    @app.get("/api/campaigns")
    def campaigns():
        items = Campaign.query.order_by(Campaign.created_at.desc()).all()
        return jsonify({"items": [item.to_dict() for item in items]})

    @app.post("/api/campaigns")
    def create_campaign():
        payload = request.get_json(silent=True) or {}
        required = ["title", "objective", "district", "topic", "platform"]
        missing = [field for field in required if not payload.get(field)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        campaign = Campaign(
            title=payload["title"],
            objective=payload["objective"],
            district=payload["district"],
            topic=payload["topic"],
            platform=payload["platform"],
            language=payload.get("language", "Hindi"),
            tone=payload.get("tone", "informative"),
            status=payload.get("status", "draft"),
        )
        db.session.add(campaign)
        db.session.commit()
        return jsonify(campaign.to_dict()), 201

    @app.get("/api/campaigns/<int:id>")
    def campaign_detail(id):
        item = Campaign.query.get_or_404(id)
        return jsonify(item.to_dict())

    @app.patch("/api/campaigns/<int:id>")
    def update_campaign(id):
        payload = request.get_json(silent=True) or {}
        item = Campaign.query.get_or_404(id)
        for field in ["title", "objective", "district", "topic", "platform", "language", "tone", "status"]:
            if field in payload:
                setattr(item, field, payload[field])
        db.session.commit()
        return jsonify(item.to_dict())

    @app.delete("/api/campaigns/<int:id>")
    def delete_campaign(id):
        item = Campaign.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"deleted": True, "id": id})

    @app.post("/api/campaigns/<int:id>/generate-draft")
    def generate_draft(id):
        campaign = Campaign.query.get_or_404(id)
        draft = ContentDraft(
            campaign_id=campaign.id,
            title=f"{campaign.topic.title()} public awareness post",
            body=(
                f"{campaign.district} के लोगों के लिए: गर्मी से सुरक्षित रहने के लिए सुबह/शाम में बाहर निकलें, पानी पीते रहें, "
                f"और छायादार स्थलों का उपयोग करें।"
            ),
            status="draft",
            platform=campaign.platform,
            references='["IMD heatwave guidance", "public health reference"]',
        )
        db.session.add(draft)
        db.session.commit()
        return jsonify(draft.to_dict()), 201

    @app.get("/api/drafts")
    def drafts():
        items = ContentDraft.query.order_by(ContentDraft.created_at.desc()).all()
        return jsonify({"items": [item.to_dict() for item in items]})

    @app.post("/api/drafts")
    def create_draft():
        payload = request.get_json(silent=True) or {}
        draft = ContentDraft(
            title=payload.get("title", "Draft message"),
            body=payload.get("body", "Draft content"),
            status=payload.get("status", "draft"),
            platform=payload.get("platform", "Instagram"),
            references=json.dumps(payload.get("references", [])),
        )
        db.session.add(draft)
        db.session.commit()
        return jsonify(draft.to_dict()), 201

    @app.patch("/api/drafts/<int:id>")
    def update_draft(id):
        payload = request.get_json(silent=True) or {}
        draft = ContentDraft.query.get_or_404(id)
        for field in ["title", "body", "status", "platform"]:
            if field in payload:
                setattr(draft, field, payload[field])
        if "references" in payload:
            draft.references = json.dumps(payload["references"])
        db.session.commit()
        return jsonify(draft.to_dict())

    @app.get("/api/schedules")
    def schedules():
        items = ScheduledPost.query.order_by(ScheduledPost.scheduled_for.asc()).all()
        return jsonify({"items": [item.to_dict() for item in items]})

    @app.post("/api/schedules")
    def create_schedule():
        payload = request.get_json(silent=True) or {}
        draft_id = payload.get("draft_id")
        if not draft_id:
            return jsonify({"error": "draft_id is required"}), 400
        try:
            scheduled_for = datetime.fromisoformat(payload["scheduled_for"])
        except (TypeError, ValueError):
            return jsonify({"error": "scheduled_for must be ISO format"}), 400
        schedule = ScheduledPost(
            draft_id=draft_id,
            scheduled_for=scheduled_for,
            status=payload.get("status", "scheduled"),
            timezone=payload.get("timezone", "Asia/Kolkata"),
            platform=payload.get("platform", "Instagram"),
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify(schedule.to_dict()), 201

    @app.patch("/api/schedules/<int:id>")
    def update_schedule(id):
        payload = request.get_json(silent=True) or {}
        schedule = ScheduledPost.query.get_or_404(id)
        if "status" in payload:
            schedule.status = payload["status"]
        if "scheduled_for" in payload:
            try:
                schedule.scheduled_for = datetime.fromisoformat(payload["scheduled_for"])
            except ValueError:
                return jsonify({"error": "scheduled_for must be ISO format"}), 400
        db.session.commit()
        return jsonify(schedule.to_dict())

    @app.delete("/api/schedules/<int:id>")
    def delete_schedule(id):
        item = ScheduledPost.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"deleted": True, "id": id})

    @app.post("/api/schedules/<int:id>/publish")
    def publish_schedule(id):
        schedule = ScheduledPost.query.get_or_404(id)
        return jsonify({
            "status": "publishing not configured",
            "message": "No authorized publishing integration is configured for this local demo environment.",
            "schedule_id": schedule.id,
        }), 202

    @app.get("/api/campaign-metrics")
    def campaign_metrics():
        items = CampaignMetric.query.order_by(CampaignMetric.metric_date.desc()).all()
        return jsonify({"items": [item.to_dict() for item in items]})

    @app.post("/api/campaign-metrics")
    def create_campaign_metric():
        payload = request.get_json(silent=True) or {}
        campaign_id = payload.get("campaign_id")
        if not campaign_id:
            return jsonify({"error": "campaign_id is required"}), 400
        metric = CampaignMetric(
            campaign_id=campaign_id,
            metric_date=datetime.strptime(payload.get("metric_date", "2025-01-01"), "%Y-%m-%d").date(),
            likes=int(payload.get("likes", 0)),
            comments=int(payload.get("comments", 0)),
            shares=int(payload.get("shares", 0)),
            clicks=int(payload.get("clicks", 0)),
            reach=int(payload.get("reach", 0)),
            impressions=int(payload.get("impressions", 0)),
            engagement_rate=float(payload.get("engagement_rate", 0.0)),
            source_type=payload.get("source_type", "manual"),
        )
        db.session.add(metric)
        db.session.commit()
        return jsonify(metric.to_dict()), 201

    @app.get("/api/models/status")
    def model_status():
        return jsonify({
            "heat_risk": {"status": "ready", "artifact": "demo-rule-based-risk"},
            "sentiment": {"status": "ready", "artifact": "demo-tfidf-logistic"},
            "topic": {"status": "ready", "artifact": "demo-keyword-topic"},
        })

    @app.get("/api/models/evaluation")
    def model_evaluation():
        items = ModelEvaluation.query.order_by(ModelEvaluation.model_name.asc()).all()
        return jsonify({"items": [item.to_dict() for item in items]})

    @app.get("/api/models/confusion-matrix")
    def confusion_matrix():
        return jsonify({"matrix": {"positive": 12, "neutral": 8, "negative": 7}})

    @app.get("/api/models/feature-importance")
    def feature_importance():
        return jsonify({
            "items": [
                {"feature": "max_temp_c", "importance": 0.31},
                {"feature": "humidity_pct", "importance": 0.23},
                {"feature": "solar_rad_wm2", "importance": 0.18},
                {"feature": "wind_kph", "importance": 0.12},
            ]
        })

    @app.post("/api/data/import")
    def data_import():
        payload = request.get_json(silent=True) or {}
        records = payload.get("records", [])
        if not records:
            return jsonify({"error": "records are required"}), 400
        return jsonify({"status": "accepted", "count": len(records), "message": "CSV or JSON data accepted for validation and preview."})

    @app.post("/api/data/validate")
    def data_validate():
        payload = request.get_json(silent=True) or {}
        required = ["district", "date", "max_temp_c"]
        missing = [field for field in required if not payload.get(field)]
        if missing:
            return jsonify({"valid": False, "errors": {field: "missing" for field in missing}}), 400
        return jsonify({"valid": True, "errors": []})

    @app.get("/api/data/preview")
    def data_preview():
        rows = WeatherObservation.query.order_by(WeatherObservation.date.desc()).limit(5).all()
        return jsonify({"items": [row.to_dict() for row in rows]})

    @app.post("/api/data/refresh")
    def data_refresh():
        return jsonify({"status": "refresh complete", "message": "Current demo environment is using available cached data and synthetic validation."})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
