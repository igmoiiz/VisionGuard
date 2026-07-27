"""Unit tests for VisionGuard Config Manager."""
import pytest
from visionguard.config.config_manager import ConfigManager, AppConfig

def test_load_default_config():
    cm = ConfigManager("config/config.yaml")
    cfg = cm.config
    assert isinstance(cfg, AppConfig)
    assert cfg.version == "1.0"
    assert len(cfg.cameras) > 0
    assert cfg.inference.engine == "yolo"

def test_config_structure():
    cm = ConfigManager("non_existent_config.yaml")
    cfg = cm.config
    assert cfg.inference.confidence_threshold == 0.35
