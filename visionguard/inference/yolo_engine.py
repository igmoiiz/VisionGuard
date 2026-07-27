"""
VisionGuard Ultralytics YOLO11 Inference Engine.
CPU-optimized PyTorch execution of YOLO object detection models.
"""

from typing import List, Optional
import numpy as np
import torch
from ultralytics import YOLO
from visionguard.core.models import Detection
from visionguard.inference.base import InferenceEngine
from visionguard.logging.logger import logger


class YOLOInferenceEngine(InferenceEngine):
    """CPU-optimized Ultralytics YOLO Inference Engine."""

    def __init__(self, model_path: str = "yolo11n.pt", cpu_threads: int = 4) -> None:
        self.model_path = model_path
        self.model: Optional[YOLO] = None
        self.cpu_threads = cpu_threads
        self._configure_torch()
        self.load_model(model_path)

    def _configure_torch(self) -> None:
        try:
            torch.set_num_threads(self.cpu_threads)
            logger.info(f"YOLOInferenceEngine: PyTorch CPU threads configured to {self.cpu_threads}")
        except Exception as e:
            logger.warning(f"Could not set PyTorch thread limit: {e}")

    def load_model(self, model_path: str) -> None:
        try:
            logger.info(f"YOLOInferenceEngine: Loading model from '{model_path}'...")
            self.model = YOLO(model_path)
            logger.info("YOLOInferenceEngine: Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load YOLO model '{model_path}': {e}")
            raise RuntimeError(f"YOLO model load error: {e}")

    def predict(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.35,
        iou_threshold: float = 0.45,
        target_classes: Optional[List[int]] = None,
    ) -> List[Detection]:
        if self.model is None:
            return []

        try:
            results = self.model.predict(
                source=image,
                conf=confidence_threshold,
                iou=iou_threshold,
                classes=target_classes,
                device="cpu",
                verbose=False,
            )

            detections: List[Detection] = []
            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None:
                    names = results[0].names
                    for box in boxes:
                        xyxy = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls_id = int(box.cls[0].cpu().numpy())
                        cls_name = names.get(cls_id, str(cls_id))

                        detections.append(
                            Detection(
                                bbox=(float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])),
                                confidence=conf,
                                class_id=cls_id,
                                class_name=cls_name,
                            )
                        )
            return detections
        except Exception as e:
            logger.error(f"YOLOInferenceEngine predict error: {e}")
            return []
