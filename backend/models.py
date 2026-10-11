from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class DatasetMetadata(db.Model):
    __tablename__ = "dataset_metadata"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    source = db.Column(db.String(255), nullable=False)
    licence = db.Column(db.String(120), default="Demonstration only")
    kind = db.Column(db.String(64), default="synthetic")
    description = db.Column(db.Text, nullable=False)
    coverage = db.Column(db.String(255), default="Rajasthan, India")
    real = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "licence": self.licence,
            "kind": self.kind,
            "description": self.description,
            "coverage": self.coverage,
            "real": self.real,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class WeatherObservation(db.Model):
    __tablename__ = "weather_observations"

    id = db.Column(db.Integer, primary_key=True)
    district = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    max_temp_c = db.Column(db.Float, nullable=False)
    min_temp_c = db.Column(db.Float, nullable=False)
    mean_temp_c = db.Column(db.Float, nullable=False)
    humidity_pct = db.Column(db.Float, nullable=True)
    wind_kph = db.Column(db.Float, nullable=True)
    solar_rad_wm2 = db.Column(db.Float, nullable=True)
    risk_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(32), default="moderate")
    source = db.Column(db.String(120), default="NASA POWER (demonstration dataset)")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.Index("ix_weather_district_date", "district", "date", unique=True),)

    def to_dict(self):
        return {
            "id": self.id,
            "district": self.district,
            "date": self.date.isoformat(),
            "max_temp_c": self.max_temp_c,
            "min_temp_c": self.min_temp_c,
            "mean_temp_c": self.mean_temp_c,
            "humidity_pct": self.humidity_pct,
            "wind_kph": self.wind_kph,
            "solar_rad_wm2": self.solar_rad_wm2,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "source": self.source,
        }


class SocialPost(db.Model):
    __tablename__ = "social_posts"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(80), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    district = db.Column(db.String(80), nullable=True)
    platform = db.Column(db.String(40), default="demo")
    topic = db.Column(db.String(64), default="general")
    sentiment = db.Column(db.String(32), default="neutral")
    engagement_score = db.Column(db.Float, default=0.0)
    reach = db.Column(db.Integer, default=0)
    is_demo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.Index("ix_social_timestamp", "timestamp"),)

    def to_dict(self):
        return {
            "id": self.id,
            "external_id": self.external_id,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "district": self.district,
            "platform": self.platform,
            "topic": self.topic,
            "sentiment": self.sentiment,
            "engagement_score": self.engagement_score,
            "reach": self.reach,
            "is_demo": self.is_demo,
        }


class PostAnalysis(db.Model):
    __tablename__ = "post_analysis"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("social_posts.id"), nullable=False)
    sentiment = db.Column(db.String(32), default="neutral")
    topic = db.Column(db.String(64), default="general")
    confidence = db.Column(db.Float, default=0.0)
    reasons = db.Column(db.Text, default="")
    classification_source = db.Column(db.String(80), default="rule-based")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "sentiment": self.sentiment,
            "topic": self.topic,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "classification_source": self.classification_source,
        }


class DistrictRisk(db.Model):
    __tablename__ = "district_risks"

    id = db.Column(db.Integer, primary_key=True)
    district = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    risk_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(32), default="moderate")
    evidence_count = db.Column(db.Integer, default=0)
    source = db.Column(db.String(120), default="synthetic weather risk")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.Index("ix_risk_district_date", "district", "date", unique=True),)

    def to_dict(self):
        return {
            "id": self.id,
            "district": self.district,
            "date": self.date.isoformat(),
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "evidence_count": self.evidence_count,
            "source": self.source,
        }


class GapAnalysis(db.Model):
    __tablename__ = "gap_analyses"

    id = db.Column(db.Integer, primary_key=True)
    district = db.Column(db.String(80), nullable=False)
    date_window = db.Column(db.String(32), nullable=False)
    risk_score = db.Column(db.Float, default=0.0)
    engagement_score = db.Column(db.Float, default=0.0)
    priority_score = db.Column(db.Float, default=0.0)
    evidence_count = db.Column(db.Integer, default=0)
    confidence = db.Column(db.String(32), default="low")
    source = db.Column(db.String(150), default="SAFETY_CONTENT")
    explanation = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "district": self.district,
            "date_window": self.date_window,
            "risk_score": self.risk_score,
            "engagement_score": self.engagement_score,
            "priority_score": self.priority_score,
            "evidence_count": self.evidence_count,
            "confidence": self.confidence,
            "source": self.source,
            "explanation": self.explanation,
        }


class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    objective = db.Column(db.String(180), nullable=False)
    district = db.Column(db.String(80), nullable=False)
    topic = db.Column(db.String(80), nullable=False)
    platform = db.Column(db.String(40), nullable=False)
    language = db.Column(db.String(40), default="Hindi")
    tone = db.Column(db.String(40), default="informative")
    status = db.Column(db.String(40), default="draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "objective": self.objective,
            "district": self.district,
            "topic": self.topic,
            "platform": self.platform,
            "language": self.language,
            "tone": self.tone,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ContentDraft(db.Model):
    __tablename__ = "content_drafts"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=True)
    title = db.Column(db.String(180), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(40), default="draft")
    platform = db.Column(db.String(40), default="Instagram")
    references = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "title": self.title,
            "body": self.body,
            "status": self.status,
            "platform": self.platform,
            "references": self.references,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ScheduledPost(db.Model):
    __tablename__ = "scheduled_posts"

    id = db.Column(db.Integer, primary_key=True)
    draft_id = db.Column(db.Integer, db.ForeignKey("content_drafts.id"), nullable=False)
    scheduled_for = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(40), default="scheduled")
    timezone = db.Column(db.String(60), default="Asia/Kolkata")
    platform = db.Column(db.String(40), default="Instagram")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "draft_id": self.draft_id,
            "scheduled_for": self.scheduled_for.isoformat() if self.scheduled_for else None,
            "status": self.status,
            "timezone": self.timezone,
            "platform": self.platform,
        }


class CampaignMetric(db.Model):
    __tablename__ = "campaign_metrics"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    metric_date = db.Column(db.Date, nullable=False)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    reach = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    source_type = db.Column(db.String(40), default="demonstration")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "metric_date": self.metric_date.isoformat(),
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "clicks": self.clicks,
            "reach": self.reach,
            "impressions": self.impressions,
            "engagement_rate": self.engagement_rate,
            "source_type": self.source_type,
        }


class ModelEvaluation(db.Model):
    __tablename__ = "model_evaluations"

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(120), nullable=False)
    metric_name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Float, default=0.0)
    details = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "model_name": self.model_name,
            "metric_name": self.metric_name,
            "value": self.value,
            "details": self.details,
        }
