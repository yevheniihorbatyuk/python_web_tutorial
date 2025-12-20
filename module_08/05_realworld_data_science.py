"""
Module 8.5: Real-World Data Science Application
==============================================

Practical data science system combining:
- SQLAlchemy ORM for structured data
- MongoDB for flexible event/log storage
- Redis for caching ML models & results
- RabbitMQ for async processing
- Real analytics and insights

Author: Senior Data Science Engineer
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA MODELS & ENUMS
# ============================================================================

class UserSegment(Enum):
    """User segmentation based on behavior."""
    DORMANT = "dormant"  # No activity for 90+ days
    ACTIVE = "active"  # Regular activity
    VIP = "vip"  # High-value users
    AT_RISK = "at_risk"  # Showing churn signals


class PredictionType(Enum):
    """Types of predictions the system makes."""
    CHURN = "churn"
    LIFETIME_VALUE = "ltv"
    NEXT_PURCHASE = "next_purchase"
    RECOMMENDATION = "recommendation"


@dataclass
class UserProfile:
    """Comprehensive user profile for analysis."""
    user_id: int
    username: str
    segment: UserSegment
    total_purchases: int
    total_spent: float
    avg_purchase_value: float
    last_purchase_days_ago: int
    account_age_days: int
    engagement_score: float
    churn_risk_score: float
    ltv_prediction: float

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "segment": self.segment.value
        }


@dataclass
class PredictionResult:
    """Result of a prediction."""
    user_id: int
    prediction_type: PredictionType
    value: float
    confidence: float
    timestamp: datetime
    features_used: List[str]

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "prediction_type": self.prediction_type.value,
            "timestamp": self.timestamp.isoformat()
        }


# ============================================================================
# ANALYTICS ENGINE
# ============================================================================

class AnalyticsEngine:
    """Core analytics engine for data science operations."""

    def __init__(self):
        self.user_metrics = {}  # In-memory cache for demo
        self.predictions_cache = {}  # Cache predictions

    def calculate_user_profile(self, user_data: Dict[str, Any]) -> UserProfile:
        """
        Calculate comprehensive user profile.
        Use case: User segmentation, personalization.
        """
        user_id = user_data["id"]
        purchases = user_data.get("purchases", [])
        registration_date = user_data.get("registration_date", datetime.utcnow())

        # Calculate metrics
        total_purchases = len(purchases)
        total_spent = sum(p["amount"] for p in purchases) if purchases else 0
        avg_purchase_value = total_spent / total_purchases if total_purchases > 0 else 0

        last_purchase = max([p["date"] for p in purchases], default=registration_date)
        last_purchase_days_ago = (datetime.utcnow() - last_purchase).days

        account_age_days = (datetime.utcnow() - registration_date).days

        # Calculate engagement score (0-100)
        engagement_score = self._calculate_engagement_score(
            total_purchases,
            last_purchase_days_ago,
            account_age_days
        )

        # Calculate churn risk (0-1)
        churn_risk = self._predict_churn_risk(
            last_purchase_days_ago,
            avg_purchase_value,
            engagement_score
        )

        # Predict LTV
        ltv = self._predict_lifetime_value(
            total_spent,
            avg_purchase_value,
            account_age_days,
            engagement_score
        )

        # Determine segment
        segment = self._determine_segment(
            last_purchase_days_ago,
            engagement_score,
            churn_risk,
            ltv
        )

        profile = UserProfile(
            user_id=user_id,
            username=user_data.get("username", f"user_{user_id}"),
            segment=segment,
            total_purchases=total_purchases,
            total_spent=total_spent,
            avg_purchase_value=avg_purchase_value,
            last_purchase_days_ago=last_purchase_days_ago,
            account_age_days=account_age_days,
            engagement_score=engagement_score,
            churn_risk_score=churn_risk,
            ltv_prediction=ltv
        )

        self.user_metrics[user_id] = profile
        return profile

    def _calculate_engagement_score(
        self,
        total_purchases: int,
        last_purchase_days_ago: int,
        account_age_days: int
    ) -> float:
        """Calculate engagement score (0-100)."""
        if account_age_days == 0:
            return 50.0

        # Recent activity weight
        recency_score = max(0, 100 - (last_purchase_days_ago * 0.5))

        # Purchase frequency
        frequency_score = min(100, (total_purchases / account_age_days) * 1000)

        # Composite score
        engagement = 0.6 * recency_score + 0.4 * frequency_score
        return round(min(100, max(0, engagement)), 2)

    def _predict_churn_risk(
        self,
        last_purchase_days_ago: int,
        avg_purchase_value: float,
        engagement_score: float
    ) -> float:
        """
        Predict churn probability (0-1).
        Simplified logistic model for demonstration.
        """
        # Features
        days_factor = min(1.0, last_purchase_days_ago / 90)  # Normalized
        value_factor = 1.0 if avg_purchase_value > 50 else 0.5
        engagement_factor = 1.0 - (engagement_score / 100)

        # Logistic function approximation
        raw_score = (days_factor * 0.4 + engagement_factor * 0.3 +
                     (1 - value_factor) * 0.3)

        # Convert to probability (0-1)
        churn_prob = 1 / (1 + np.exp(-5 * (raw_score - 0.5)))
        return round(float(churn_prob), 3)

    def _predict_lifetime_value(
        self,
        total_spent: float,
        avg_purchase_value: float,
        account_age_days: int,
        engagement_score: float
    ) -> float:
        """
        Predict customer lifetime value.
        Use case: Budget allocation, marketing spend decisions.
        """
        if account_age_days == 0:
            return avg_purchase_value

        # Historical spending pattern
        daily_spending = total_spent / account_age_days if account_age_days > 0 else avg_purchase_value

        # Project 365 days
        base_ltv = daily_spending * 365

        # Adjust based on engagement
        engagement_multiplier = 0.5 + (engagement_score / 100)
        ltv = base_ltv * engagement_multiplier

        # Cap at reasonable values
        ltv = min(10000, max(0, ltv))
        return round(ltv, 2)

    def _determine_segment(
        self,
        last_purchase_days_ago: int,
        engagement_score: float,
        churn_risk: float,
        ltv: float
    ) -> UserSegment:
        """Determine user segment based on characteristics."""
        # VIP: High engagement, high LTV
        if engagement_score >= 70 and ltv >= 500:
            return UserSegment.VIP

        # At-risk: High churn probability
        if churn_risk >= 0.7:
            return UserSegment.AT_RISK

        # Dormant: No recent activity
        if last_purchase_days_ago >= 90 and engagement_score < 30:
            return UserSegment.DORMANT

        # Active: Regular engagement
        return UserSegment.ACTIVE


# ============================================================================
# ML MODEL MANAGER
# ============================================================================

class MLModelManager:
    """Manage ML model predictions with caching."""

    def __init__(self, cache=None):
        self.cache = cache  # Redis cache if available
        self.model_version = "1.0"

    def predict(
        self,
        prediction_type: PredictionType,
        features: Dict[str, float]
    ) -> PredictionResult:
        """
        Get prediction from model.
        Would normally load serialized model from disk/cache.
        """
        # In real system: load model from cache/disk
        # For demo: use simple heuristic models

        if prediction_type == PredictionType.CHURN:
            return self._predict_churn(features)
        elif prediction_type == PredictionType.LIFETIME_VALUE:
            return self._predict_ltv(features)
        elif prediction_type == PredictionType.NEXT_PURCHASE:
            return self._predict_next_purchase(features)
        else:
            raise ValueError(f"Unknown prediction type: {prediction_type}")

    def _predict_churn(self, features: Dict[str, float]) -> Tuple[float, float]:
        """Simplified churn prediction."""
        # Feature importance in simplified model
        days_inactive = features.get("days_since_purchase", 60)
        engagement = features.get("engagement_score", 50)

        # Score
        score = (days_inactive / 100) * 0.5 - (engagement / 100) * 0.5 + 0.5
        prediction = max(0, min(1, score))
        confidence = 0.85  # Model confidence

        return prediction, confidence

    def _predict_ltv(self, features: Dict[str, float]) -> Tuple[float, float]:
        """Simplified LTV prediction."""
        avg_purchase = features.get("avg_purchase_value", 50)
        frequency = features.get("purchase_frequency", 0.1)
        engagement = features.get("engagement_score", 50)

        # Predict 365-day LTV
        prediction = avg_purchase * 52 * frequency * (engagement / 50)
        confidence = 0.80

        return min(5000, prediction), confidence

    def _predict_next_purchase(self, features: Dict[str, float]) -> Tuple[float, float]:
        """Predict days until next purchase."""
        days_inactive = features.get("days_since_purchase", 30)
        purchase_cycle = features.get("purchase_cycle_days", 30)
        engagement = features.get("engagement_score", 50)

        # Predict next purchase in X days
        prediction = days_inactive + (purchase_cycle * (100 - engagement) / 100)
        confidence = 0.75

        return max(1, prediction), confidence


# ============================================================================
# RECOMMENDATION ENGINE
# ============================================================================

class RecommendationEngine:
    """Content/product recommendations using collaborative filtering."""

    def __init__(self):
        self.product_embeddings = self._load_embeddings()

    def _load_embeddings(self) -> Dict[str, np.ndarray]:
        """Load pre-computed product embeddings."""
        # Mock embeddings for demo
        return {
            f"product_{i}": np.random.randn(32)  # 32-dimensional
            for i in range(1, 21)
        }

    def get_recommendations(
        self,
        user_id: int,
        user_profile: UserProfile,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get personalized product recommendations.
        Use case: Increase AOV, improve retention.
        """
        recommendations = []

        # Strategy based on segment
        if user_profile.segment == UserSegment.VIP:
            # Premium recommendations for VIP
            base_score = 0.9
            product_ids = [f"product_{i}" for i in range(1, 11)]
        elif user_profile.segment == UserSegment.AT_RISK:
            # Re-engagement offers
            base_score = 0.8
            product_ids = [f"product_{i}" for i in range(11, 21)]
        else:
            # Standard recommendations
            base_score = 0.7
            product_ids = [f"product_{i}" for i in range(1, 21)]

        # Generate recommendations
        for i, product_id in enumerate(product_ids[:limit]):
            score = base_score - (i * 0.05)  # Decrease with rank
            recommendations.append({
                "product_id": product_id,
                "relevance_score": max(0, score),
                "reason": self._get_recommendation_reason(user_profile.segment)
            })

        return recommendations

    def _get_recommendation_reason(self, segment: UserSegment) -> str:
        """Get explanation for recommendation."""
        reasons = {
            UserSegment.VIP: "Premium product for valued customer",
            UserSegment.ACTIVE: "Based on your purchase history",
            UserSegment.AT_RISK: "Special offer to delight you",
            UserSegment.DORMANT: "We miss you - here's something special"
        }
        return reasons.get(segment, "Recommended for you")


# ============================================================================
# REPORTING & INSIGHTS
# ============================================================================

class InsightsGenerator:
    """Generate actionable business insights."""

    def __init__(self, analytics_engine: AnalyticsEngine):
        self.analytics = analytics_engine

    def generate_segment_report(self) -> Dict[str, Any]:
        """
        Generate user segmentation report.
        Use case: Marketing strategy, resource allocation.
        """
        profiles = list(self.analytics.user_metrics.values())

        if not profiles:
            return {}

        segment_counts = {}
        for segment in UserSegment:
            count = sum(1 for p in profiles if p.segment == segment)
            segment_counts[segment.value] = count

        # Calculate aggregate metrics
        avg_engagement = np.mean([p.engagement_score for p in profiles])
        avg_churn_risk = np.mean([p.churn_risk_score for p in profiles])
        total_ltv = sum(p.ltv_prediction for p in profiles)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_users": len(profiles),
            "segments": segment_counts,
            "metrics": {
                "avg_engagement_score": round(float(avg_engagement), 2),
                "avg_churn_risk": round(float(avg_churn_risk), 3),
                "total_predicted_ltv": round(float(total_ltv), 2)
            },
            "insights": self._generate_insights(profiles)
        }

    def _generate_insights(self, profiles: List[UserProfile]) -> List[str]:
        """Generate actionable insights."""
        insights = []

        # At-risk users insight
        at_risk = [p for p in profiles if p.segment == UserSegment.AT_RISK]
        if len(at_risk) > 0:
            insights.append(
                f"⚠️ {len(at_risk)} users at churn risk. "
                f"Consider retention campaigns."
            )

        # VIP insight
        vips = [p for p in profiles if p.segment == UserSegment.VIP]
        if len(vips) > 0:
            vip_ltv = sum(p.ltv_prediction for p in vips)
            insights.append(
                f"💎 {len(vips)} VIP users represent ${vip_ltv:.0f} "
                f"of projected revenue."
            )

        # Dormant users insight
        dormant = [p for p in profiles if p.segment == UserSegment.DORMANT]
        if len(dormant) > 0:
            insights.append(
                f"😴 {len(dormant)} dormant users. "
                f"Re-engagement campaign recommended."
            )

        return insights


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def demonstrate_data_science_system():
    """Demonstrate integrated data science system."""

    logger.info("\n" + "="*80)
    logger.info("Real-World Data Science Application")
    logger.info("="*80 + "\n")

    # Initialize components
    analytics = AnalyticsEngine()
    ml_models = MLModelManager()
    recommendations = RecommendationEngine()
    insights = InsightsGenerator(analytics)

    # ---- SCENARIO 1: PROCESS NEW USER DATA ----
    logger.info("[1] Processing User Data & Generating Profiles")
    logger.info("-" * 80)

    sample_users = [
        {
            "id": 1,
            "username": "power_user",
            "registration_date": datetime.utcnow() - timedelta(days=365),
            "purchases": [
                {"amount": 100, "date": datetime.utcnow() - timedelta(days=5)},
                {"amount": 150, "date": datetime.utcnow() - timedelta(days=15)},
                {"amount": 80, "date": datetime.utcnow() - timedelta(days=25)},
            ]
        },
        {
            "id": 2,
            "username": "occasional_buyer",
            "registration_date": datetime.utcnow() - timedelta(days=180),
            "purchases": [
                {"amount": 50, "date": datetime.utcnow() - timedelta(days=60)},
            ]
        },
        {
            "id": 3,
            "username": "dormant_user",
            "registration_date": datetime.utcnow() - timedelta(days=365),
            "purchases": [
                {"amount": 75, "date": datetime.utcnow() - timedelta(days=120)},
            ]
        },
    ]

    profiles = []
    for user_data in sample_users:
        profile = analytics.calculate_user_profile(user_data)
        profiles.append(profile)

        logger.info(f"\n  User: {profile.username}")
        logger.info(f"    Segment: {profile.segment.value}")
        logger.info(f"    Engagement: {profile.engagement_score}/100")
        logger.info(f"    Churn Risk: {profile.churn_risk_score:.1%}")
        logger.info(f"    Predicted LTV: ${profile.ltv_prediction:.2f}")

    # ---- SCENARIO 2: ML PREDICTIONS ----
    logger.info("\n[2] ML Model Predictions")
    logger.info("-" * 80)

    for profile in profiles[:2]:
        logger.info(f"\n  {profile.username}:")

        # Churn prediction
        churn_pred = ml_models.predict(
            PredictionType.CHURN,
            {
                "days_since_purchase": profile.last_purchase_days_ago,
                "engagement_score": profile.engagement_score
            }
        )
        logger.info(f"    Churn probability: {churn_pred[0]:.1%} (confidence: {churn_pred[1]:.0%})")

        # LTV prediction
        ltv_pred = ml_models.predict(
            PredictionType.LIFETIME_VALUE,
            {
                "avg_purchase_value": profile.avg_purchase_value,
                "purchase_frequency": 1 if profile.total_purchases > 0 else 0,
                "engagement_score": profile.engagement_score
            }
        )
        logger.info(f"    LTV prediction: ${ltv_pred[0]:.2f} (confidence: {ltv_pred[1]:.0%})")

    # ---- SCENARIO 3: RECOMMENDATIONS ----
    logger.info("\n[3] Personalized Recommendations")
    logger.info("-" * 80)

    for profile in profiles[:2]:
        logger.info(f"\n  {profile.username}:")
        recs = recommendations.get_recommendations(
            profile.user_id,
            profile,
            limit=3
        )
        for i, rec in enumerate(recs, 1):
            logger.info(f"    {i}. {rec['product_id']}: "
                       f"relevance {rec['relevance_score']:.0%} - "
                       f"{rec['reason']}")

    # ---- SCENARIO 4: BUSINESS INSIGHTS ----
    logger.info("\n[4] Business Insights & Reporting")
    logger.info("-" * 80)

    report = insights.generate_segment_report()

    logger.info(f"\n  Total Users: {report['total_users']}")
    logger.info(f"  Segment Distribution:")
    for segment, count in report['segments'].items():
        logger.info(f"    - {segment}: {count}")

    logger.info(f"\n  Key Metrics:")
    for metric, value in report['metrics'].items():
        if metric == 'total_predicted_ltv':
            logger.info(f"    - {metric}: ${value:.2f}")
        else:
            logger.info(f"    - {metric}: {value}")

    logger.info(f"\n  Insights:")
    for insight in report['insights']:
        logger.info(f"    {insight}")

    logger.info("\n" + "="*80)
    logger.info("✓ Data science system demonstration completed")
    logger.info("="*80 + "\n")


if __name__ == "__main__":
    demonstrate_data_science_system()
