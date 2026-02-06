from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class EventORM(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)

    score = relationship(
        "ScoreORM",
        back_populates="event",
        uselist=False,
        cascade="all, delete-orphan",
    )
    reviews = relationship("ReviewORM", back_populates="event", cascade="all, delete-orphan")


class ScoreORM(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False, unique=True)
    signal_strength = Column(Float, nullable=False)
    historical_rarity = Column(Float, nullable=False)
    trend_acceleration = Column(Float, nullable=False)
    cross_source_presence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)

    event = relationship("EventORM", back_populates="score")


class ReviewORM(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    reviewer = Column(String, nullable=False)
    note = Column(Text, nullable=False)
    reviewed_at = Column(DateTime, nullable=False)

    event = relationship("EventORM", back_populates="reviews")
