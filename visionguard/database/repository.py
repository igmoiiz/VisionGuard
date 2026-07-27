"""
VisionGuard Repository Pattern (DAO).
Provides persistent CRUD operations for Events, Cameras, and System Metrics.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from visionguard.core.models import Event, PerformanceMetrics
from visionguard.database.models import EventDB, PerformanceMetricDB
from visionguard.logging.logger import logger


class EventRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def save_event(self, event: Event) -> Optional[EventDB]:
        session: Session = self.session_factory()
        try:
            db_event = EventDB(
                event_id=event.event_id,
                timestamp=event.timestamp,
                camera_id=event.camera_id,
                event_type=event.event_type,
                severity=event.severity.value,
                object_id=event.object_id,
                object_class=event.object_class,
                confidence=event.confidence,
                zone_id=event.zone_id,
                zone_name=event.zone_name,
                snapshot_path=event.snapshot_path,
                metadata_json=event.metadata,
            )
            session.add(db_event)
            session.commit()
            session.refresh(db_event)
            return db_event
        except Exception as e:
            session.rollback()
            logger.error(f"EventRepository: Failed to save event: {e}")
            return None
        finally:
            session.close()

    def get_events(
        self,
        camera_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EventDB]:
        session: Session = self.session_factory()
        try:
            query = session.query(EventDB)
            if camera_id:
                query = query.filter(EventDB.camera_id == camera_id)
            if event_type:
                query = query.filter(EventDB.event_type == event_type)
            results = query.order_by(EventDB.timestamp.desc()).offset(offset).limit(limit).all()
            return results
        finally:
            session.close()


class MetricsRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def save_metrics(self, metrics: PerformanceMetrics) -> None:
        session: Session = self.session_factory()
        try:
            db_m = PerformanceMetricDB(
                timestamp=metrics.timestamp,
                fps=metrics.fps,
                frame_processing_latency_ms=metrics.frame_processing_latency_ms,
                detection_latency_ms=metrics.detection_latency_ms,
                tracking_latency_ms=metrics.tracking_latency_ms,
                cpu_usage_pct=metrics.cpu_usage_pct,
                memory_mb=metrics.memory_mb,
                frame_drop_count=metrics.frame_drop_count,
            )
            session.add(db_m)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"MetricsRepository: Save error: {e}")
        finally:
            session.close()
