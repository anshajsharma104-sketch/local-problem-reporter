from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String, nullable=True)
    is_authority = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    issues = relationship("Issue", back_populates="reporter")


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    description = Column(Text)
    issue_type = Column(String, index=True)  # road_damage, garbage, water_leak, landslide, traffic, etc.
    image_path = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    location_description = Column(String)
    street_address = Column(String, nullable=True)  # Cached reverse geocoded address
    priority_score = Column(Float, default=0.0)
    priority_level = Column(String, default="medium")  # low, medium, high, critical
    status = Column(String, default="reported")  # reported, investigating, resolved
    ai_confidence = Column(Float, default=0.0)
    ai_detected_objects = Column(String)  # JSON string of detected objects
    upvotes = Column(Integer, default=0)  # Priority votes for reported/investigating
    satisfaction_votes = Column(Integer, default=0)  # Satisfaction votes for resolved
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    reporter = relationship("User", back_populates="issues")
    updates = relationship("IssueUpdate", back_populates="issue", cascade="all, delete-orphan")


class IssueUpdate(Base):
    __tablename__ = "issue_updates"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    authority_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status_update = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    issue = relationship("Issue", back_populates="updates")


class IssueUpvote(Base):
    __tablename__ = "issue_upvotes"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    vote_type = Column(String, default="priority")  # 'priority' or 'satisfaction'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Ensure each user can only vote once per type per issue
    __table_args__ = (
        UniqueConstraint('issue_id', 'user_id', 'vote_type', name='unique_issue_vote_per_type'),
    )


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    issue_type = Column(String)
    count = Column(Integer, default=0)
    avg_priority = Column(Float, default=0.0)
    resolution_rate = Column(Float, default=0.0)
