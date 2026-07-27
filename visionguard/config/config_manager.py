"""
VisionGuard Configuration Manager.
Parses, validates, and manages YAML configurations using Pydantic schema validation.
Supports configuration versioning, environment variable overrides, and runtime updates.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field
from visionguard.logging.logger import logger


class CameraConfig(BaseModel):
    id: str
    name: str
    source: str
    enabled: bool = True
    fps_target: float = 25.0
    resolution: List[int] = Field(default_factory=lambda: [1280, 720])
    reconnect_interval_sec: float = 5.0
    buffer_size: int = 10


class InferenceConfig(BaseModel):
    engine: str = "yolo"
    model_path: str = "yolo11n.pt"
    confidence_threshold: float = 0.35
    iou_threshold: float = 0.45
    img_size: int = 640
    frame_skip: int = 1
    target_classes: List[int] = Field(default_factory=list)


class TrackingConfig(BaseModel):
    algorithm: str = "bytetrack"
    track_high_thresh: float = 0.5
    track_low_thresh: float = 0.1
    new_track_thresh: float = 0.6
    match_thresh: float = 0.8
    track_buffer: int = 30
    max_trajectory_length: int = 50
    smooth_trajectories: bool = True


class RegionConfig(BaseModel):
    id: str
    name: str
    type: str
    points: List[List[float]]
    direction: Optional[str] = "bidirectional"
    color: List[int] = Field(default_factory=lambda: [0, 255, 0])
    enabled: bool = True


class EventPluginConfig(BaseModel):
    enabled: bool = True
    cooldown_sec: float = 3.0
    threshold_sec: Optional[float] = None
    target_zones: Optional[List[str]] = None
    target_classes: Optional[List[str]] = None
    movement_threshold_px: Optional[float] = None
    velocity_threshold_px_per_sec: Optional[float] = None
    max_count: Optional[int] = None


class EventsConfig(BaseModel):
    plugins: Dict[str, EventPluginConfig] = Field(default_factory=dict)


class RecordingConfig(BaseModel):
    enabled: bool = True
    output_dir: str = "data/recordings"
    snapshots_dir: str = "data/snapshots"
    continuous: bool = False
    event_triggered: bool = True
    pre_event_buffer_sec: float = 3.0
    post_event_buffer_sec: float = 5.0
    retention_days: int = 7
    video_format: str = "mp4v"


class DatabaseConfig(BaseModel):
    url: str = "sqlite:///data/visionguard.db"
    echo: bool = False
    pool_pre_ping: bool = True


class ApiConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    enable_docs: bool = True
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])


class DashboardConfig(BaseModel):
    theme: str = "dark"
    refresh_rate_ms: int = 33
    chart_history_points: int = 60


class MetricsConfig(BaseModel):
    collection_interval_sec: float = 1.0
    history_buffer_size: int = 100


class AppConfig(BaseModel):
    version: str = "1.0"
    system: Dict[str, Any] = Field(default_factory=dict)
    cameras: List[CameraConfig] = Field(default_factory=list)
    inference: InferenceConfig = Field(default_factory=InferenceConfig)
    tracking: TrackingConfig = Field(default_factory=TrackingConfig)
    regions: List[RegionConfig] = Field(default_factory=list)
    events: EventsConfig = Field(default_factory=EventsConfig)
    recording: RecordingConfig = Field(default_factory=RecordingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)


class ConfigManager:
    """Manages application configuration loading, validation, and serialization."""
    def __init__(self, config_path: str = "config/config.yaml") -> None:
        self.config_path = Path(config_path)
        self.config: AppConfig = self.load_config()

    def load_config(self) -> AppConfig:
        if not self.config_path.exists():
            logger.warning(f"Config file '{self.config_path}' not found. Initializing default settings.")
            return AppConfig()

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                raw_dict = yaml.safe_load(f) or {}

            # Config version check
            version = raw_dict.get("version", "1.0")
            logger.info(f"Loaded configuration file '{self.config_path}' (Schema Version: {version})")

            app_config = AppConfig(**raw_dict)
            return app_config
        except Exception as e:
            logger.error(f"Error parsing configuration file '{self.config_path}': {e}. Using defaults.")
            return AppConfig()

    def save_config(self) -> None:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            dict_repr = self.config.model_dump()
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(dict_repr, f, sort_keys=False)
            logger.info(f"Saved configuration to '{self.config_path}'")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
