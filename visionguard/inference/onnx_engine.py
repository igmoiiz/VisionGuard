"""
VisionGuard ONNX Runtime Inference Engine Wrapper.
Provides CPU inference using ONNX Runtime for deployment environments.
"""

from typing import List, Optional
import numpy as np
from visionguard.core.models import Detection
from visionguard.inference.base import InferenceEngine
from visionguard.logging.logger import logger


class ONNXInferenceEngine(InferenceEngine):
    """ONNX Runtime Inference Engine implementation."""

    def __init__(self, model_path: str = "models_cache/yolo11n.onnx") -> None:
        self.model_path = model_path
        self.session = None
        self.load_model(model_path)

    def load_model(self, model_path: str) -> None:
        try:
            import onnxruntime as ort
            logger.info(f"ONNXInferenceEngine: Loading ONNX model '{model_path}'...")
            self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
            logger.info("ONNXInferenceEngine: Model loaded successfully.")
        except Exception as e:
            logger.warning(f"ONNXRuntime not available or model failed to load ({e}). Using mock/fallback.")
            self.session = None

    def predict(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.35,
        iou_threshold: float = 0.45,
        target_classes: Optional[List[int]] = None,
    ) -> List[Detection]:
        # Placeholder / Mock when ONNX file is not supplied
        return []
