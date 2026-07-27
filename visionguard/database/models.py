"""
VisionGuard SQLAlchemy ORM Database Models.
Defines schemas for camera sources, event logs, detection statistics, and performance metrics.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, Text, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CameraDB(Base):
    __tablename__ = "cameras"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    source = Column(String(255), nullable=False)
    enabled = Column(Boolean, default=True)
    fps_target = Column(Float, default=25.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class EventDB(Base):
    __tablename__ = "events"

    event_id = Column(String(36), primary_key=True)
    timestamp = Column(Float, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    camera_id = Column(String(50), index=True, nullable=False)
    event_type = Column(String(50), index=True, nullable=False)
    severity = Column(String(20), default="warning")
    object_id = Column(Integer, nullable=True)
    object_class = Column(String(50), nullable=True)
    confidence = Column(Float, default=1.0)
    zone_id = Column(String(50), nullable=True)
    zone_name = Column(String(100), nullable=True)
    snapshot_path = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)


class DetectionStatDB(Base):
    __tablename__ = "detection_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Float, index=True, nullable=False)
    camera_id = Column(String(50), index=True, nullable=False)
    class_name = Column(String(50), nullable=False)
    count = Column(Integer, default=1)


class PerformanceMetricDB(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Float, index=True, nullable=False)
    fps = Column(Float, default=0.0)
    frame_processing_latency_ms = Column(Float, default=0.0)
    detection_latency_ms = Column(Float, default=0.0)
    tracking_latency_ms = Column(Float, default=0.0)
    cpu_usage_pct = Column(Float, default=0.0)
    memory_mb = Column(Float, default=0.0)
    frame_drop_count = Column(Integer, default=0)
