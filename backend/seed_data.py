from datetime import date, datetime, timedelta

from backend.models import (
    Campaign,
    CampaignMetric,
    ContentDraft,
    DatasetMetadata,
    DistrictRisk,
    GapAnalysis,
    ModelEvaluation,
    PostAnalysis,
    ScheduledPost,
    SocialPost,
    WeatherObservation,
    db,
)


def _risk_from_weather(max_temp_c, humidity_pct, wind_kph):
    score = 35 + (max_temp_c - 30) * 2.6 + max(0, 60 - humidity_pct) * 0.4 + max(0, 18 - wind_kph) * 1.3
    score = max(0, min(100, score))
    if score >= 75:
        label = "extreme"
    elif score >= 55:
        label = "high"
    elif score >= 35:
        label = "moderate"
    else:
        label = "low"
    return round(score, 1), label


def _classify_text(text):
    lower = text.lower()
    if any(word in lower for word in ["heat", "temperature", "suffocating", "sun", "boiling"]):
        topic = "heat_discomfort"
    elif any(word in lower for word in ["water", "hydration", "drink", "thirst"]):
        topic = "hydration"
    elif any(word in lower for word in ["advisory", "safety", "cooling", "shade"]):
        topic = "safety_advisories"
    elif any(word in lower for word in ["hospital", "help", "need", "support"]):
        topic = "requests_for_help"
    elif any(word in lower for word in ["power", "water supply", "facility", "school", "community"]):
        topic = "public_facilities"
    else:
        topic = "general_heat_news"

    if any(word in lower for word in ["worried", "bad", "stress", "danger", "sick", "exhausted"]):
        sentiment = "negative"
    elif any(word in lower for word in ["safe", "relief", "good", "helpful", "cool"]):
        sentiment = "positive"
    else:
        sentiment = "neutral"

    confidence = 0.72 if topic and sentiment else 0.45
    return sentiment, topic, confidence


def seed_demo_data():
    existing = DatasetMetadata.query.first()
    if existing:
        return

    districts = ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur", "Alwar"]
    base_date = date.today() - timedelta(days=29)

    features = []
    for offset in range(30):
        day = base_date + timedelta(days=offset)
        for district in districts:
            temp_base = 38 + (len(district) % 5)
            humid = 28 + (offset % 12) * 3 + (len(district) % 4)
            wind = 8 + (offset % 7)
            max_temp = temp_base + (offset % 6) + 4
            min_temp = max(22, temp_base - 11 + (offset % 3))
            mean_temp = (max_temp + min_temp) / 2
            risk_score, risk_level = _risk_from_weather(max_temp, humid, wind)
            features.append(
                WeatherObservation(
                    district=district,
                    date=day,
                    max_temp_c=max_temp,
                    min_temp_c=min_temp,
                    mean_temp_c=mean_temp,
                    humidity_pct=humid,
                    wind_kph=wind,
                    solar_rad_wm2=560 + (offset * 5),
                    risk_score=risk_score,
                    risk_level=risk_level,
                    source="NASA POWER (demonstration dataset)",
                )
            )

    db.session.add_all(features)

    for day_index in range(10):
        day = base_date + timedelta(days=day_index)
        for district in districts:
            risk = 48 + (day_index * 2) + (len(district) % 9)
            label = "high" if risk >= 60 else "moderate"
            db.session.add(
                DistrictRisk(
                    district=district,
                    date=day,
                    risk_score=min(100, risk),
                    risk_level=label,
                    evidence_count=5,
                    source="weather risk synthesis",
                )
            )

    social_seed = [
        "Heat is unbearable in Jaipur today. We need public cooling shelters and more water supply support.",
        "Kota residents are asking for hydration and shade safety plans as temperatures rise.",
        "Jodhpur residents are worried about heat stress and children walking to school without water.",
        "Bikaner community needs advisories on heat safety and emergency cooling facilities.",
        "The afternoon heat has been brutal in Alwar; please share safe drinking water points.",
        "Ajmer is feeling the heat; we need public awareness campaigns on heatstroke prevention.",
        "This heatwave is dangerous for elderly citizens, please share cooling access information.",
        "Support workers in Udaipur need more shade and hydration stations during peak afternoon heat.",
    ]

    for index, content in enumerate(social_seed):
        timestamp = datetime.utcnow() - timedelta(days=index % 7)
        district = districts[index % len(districts)]
        sentiment, topic, confidence = _classify_text(content)
        post = SocialPost(
            external_id=f"demo-{index + 1}",
            text=content,
            timestamp=timestamp,
            district=district,
            platform="demo-social",
            topic=topic,
            sentiment=sentiment,
            engagement_score=24 + (index * 7) % 38,
            reach=400 + index * 60,
            is_demo=True,
        )
        db.session.add(post)
        db.session.flush()
        db.session.add(
            PostAnalysis(
                post_id=post.id,
                sentiment=sentiment,
                topic=topic,
                confidence=confidence,
                reasons="Rule-based classification using heat and safety keywords.",
                classification_source="rule-based",
            )
        )

    metadata_rows = [
        DatasetMetadata(
            name="rajasthan_weather_demo",
            source="NASA POWER (offline demo data benchmark)",
            licence="Demonstration and academic use",
            kind="weather",
            description="Synthetic Rajasthan weather observations used for offline heat-risk exploration.",
            coverage="Jaipur, Jodhpur, Kota, Bikaner, Ajmer, Udaipur, Alwar; 30-day window",
            real=False,
        ),
        DatasetMetadata(
            name="heat_safety_demo_posts",
            source="Synthesized social-media listening dataset",
            licence="Academic demonstration data",
            kind="social",
            description="Synthetic heat-related social posts to demo classification and awareness analysis.",
            coverage="Rajasthan districts; public discussion sample",
            real=False,
        ),
    ]
    db.session.add_all(metadata_rows)

    gap_rows = [
        GapAnalysis(
            district="Jaipur",
            date_window="last 7 days",
            risk_score=86,
            engagement_score=28,
            priority_score=0.62,
            evidence_count=9,
            confidence="moderate",
            source="heat-risk × safety-content engagement",
            explanation="High heat risk and moderate safety engagement create a strong communication need in Jaipur.",
        ),
        GapAnalysis(
            district="Jodhpur",
            date_window="last 7 days",
            risk_score=91,
            engagement_score=18,
            priority_score=0.74,
            evidence_count=7,
            confidence="moderate",
            source="heat-risk × safety-content engagement",
            explanation="Very high heat exposure with limited identifiable safety-content engagement suggests a high-priority awareness gap.",
        ),
        GapAnalysis(
            district="Kota",
            date_window="last 7 days",
            risk_score=71,
            engagement_score=46,
            priority_score=0.38,
            evidence_count=6,
            confidence="moderate",
            source="heat-risk × safety-content engagement",
            explanation="Heat risk remains elevated, but safety discussions are comparatively stronger, reducing communication urgency.",
        ),
    ]
    db.session.add_all(gap_rows)

    campaigns = [
        Campaign(
            title="Jaipur hydration awareness",
            objective="Increase safe hydration awareness",
            district="Jaipur",
            topic="hydration",
            platform="Instagram",
            language="Hindi",
            tone="informative",
            status="approved",
        ),
        Campaign(
            title="Jodhpur cooling access",
            objective="Promote cooling shelters and shade support",
            district="Jodhpur",
            topic="public_facilities",
            platform="WhatsApp",
            language="Hindi",
            tone="supportive",
            status="scheduled",
        ),
    ]
    db.session.add_all(campaigns)
    db.session.flush()

    draft1 = ContentDraft(
        campaign_id=campaigns[0].id,
        title="Hydration reminder",
        body="ठण्डे पेय, Shade, और पानी की उपलब्धता पर ध्यान दें। गर्मी के दौरान सुबह/शाम में बाहर निकलें।",
        status="approved",
        platform="Instagram",
        references='["IMD heatwave guidance", "local city cooling desk"]',
    )
    db.session.add(draft1)
    db.session.flush()
    db.session.add(
        ScheduledPost(
            draft_id=draft1.id,
            scheduled_for=datetime.utcnow() + timedelta(days=2),
            status="scheduled",
            timezone="Asia/Kolkata",
            platform="Instagram",
        )
    )
    db.session.add(
        CampaignMetric(
            campaign_id=campaigns[0].id,
            metric_date=date.today() - timedelta(days=1),
            likes=420,
            comments=53,
            shares=88,
            clicks=120,
            reach=6000,
            impressions=8200,
            engagement_rate=0.12,
            source_type="demonstration",
        )
    )
    db.session.add(
        CampaignMetric(
            campaign_id=campaigns[1].id,
            metric_date=date.today() - timedelta(days=2),
            likes=310,
            comments=29,
            shares=71,
            clicks=93,
            reach=5200,
            impressions=7600,
            engagement_rate=0.09,
            source_type="demonstration",
        )
    )

    db.session.add_all(
        [
            ModelEvaluation(model_name="heat_risk_baseline", metric_name="macro_f1", value=0.82, details='{"dataset": "demo-weather", "notes": "rule-based risk indicator"}'),
            ModelEvaluation(model_name="sentiment_baseline", metric_name="macro_f1", value=0.71, details='{"dataset": "demo-social", "notes": "TF-IDF + Logistic Regression"}'),
            ModelEvaluation(model_name="topic_classifier", metric_name="macro_f1", value=0.68, details='{"dataset": "demo-social", "notes": "rule-based topic detection"}'),
        ]
    )

    db.session.commit()
