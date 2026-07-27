"""
VisionGuard Abstract Inference Engine Interface.
Satisfies Recommendation #3 (Inference Engine Layer). Allows swapping execution backends
(Ultralytics YOLO, ONNX Runtime, OpenVINO, TensorRT) without downstream pipeline changes.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from visionguard.core.models import Detection


class InferenceEngine(ABC):
    """Abstract Base Class for AI Object Detection Engines."""

    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """Loads model weights into memory."""
        pass

    @abstractmethod
    def predict(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.35,
        iou_threshold: float = 0.45,
        target_classes: Optional[List[int]] = None,
    ) -> List[Detection]:
        """Performs object detection inference on an input frame."""
        pass
