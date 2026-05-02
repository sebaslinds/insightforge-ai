from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    user_id      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
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

    events = relationship("Event", back_populates="user")


class Event(Base):
    __tablename__ = "events"

    event_id    = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String, ForeignKey("users.user_id"), nullable=False)
    timestamp   = Column(DateTime, default=datetime.utcnow)
    event_type  = Column(String, nullable=False)  # page_view / feature_used / ...
    feature_name= Column(String, nullable=True)
    session_id  = Column(String, nullable=True)

    user = relationship("User", back_populates="events")
