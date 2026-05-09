from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    user_id      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id    = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    signup_date  = Column(DateTime, nullable=False)
    plan         = Column(String, nullable=False)   # free / pro / enterprise
    country      = Column(String, nullable=True)
    segment      = Column(String, nullable=True)    # power_user / casual / at_risk / dormant

    # ML Features
    session_count_30d        = Column(Integer, default=0)
    session_count_7d         = Column(Integer, default=0)
    avg_session_duration_min = Column(Float, default=0.0)
    feature_breadth          = Column(Integer, default=0)
    days_since_last_use      = Column(Integer, default=0)
    engagement_score         = Column(Float, default=0.0)

    # Predictions
    churn_score  = Column(Float, nullable=True)
    churned      = Column(Boolean, default=False)

    # Acquisition
    acquisition_cost    = Column(Float, default=0.0)
    acquisition_channel = Column(String, nullable=True) # google_ads / linkedin / organic / etc.

    events = relationship("Event", back_populates="user")

class Event(Base):
    __tablename__ = "events"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(String, ForeignKey("users.user_id"))
    tenant_id  = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    event_type = Column(String)  # page_view / feature_use / session_start
    feature    = Column(String, nullable=True)
    timestamp  = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="events")

class BusinessRule(Base):
    __tablename__ = "business_rules"

    id           = Column(Integer, primary_key=True)
    tenant_id    = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    name         = Column(String, nullable=False)
    description  = Column(Text, nullable=False)
    enabled      = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
    rule_type    = Column(String, default="ai_suggested") # manual / ai_suggested
    lang         = Column(String, default="en") # en / fr

class Notification(Base):
    __tablename__ = "notifications"

    id          = Column(Integer, primary_key=True)
    tenant_id   = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    title       = Column(String, nullable=False)
    message     = Column(Text, nullable=False)
    type        = Column(String, default="info") # info / warning / success / danger
    read        = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id           = Column(Integer, primary_key=True)
    user_id      = Column(String, ForeignKey("users.user_id"))
    feature      = Column(String, nullable=False)
    is_helpful   = Column(Boolean, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)
    tenant_id    = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
