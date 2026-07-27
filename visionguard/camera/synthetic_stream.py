"""
VisionGuard Synthetic Video Stream Generator.
Generates animated synthetic video frames with moving shapes (people, vehicles)
for testing when a physical camera device is absent or inaccessible.
"""

from queue import Queue
import time
from threading import Thread
from typing import List, Optional
import cv2
import numpy as np
from visionguard.camera.base_stream import BaseStream
from visionguard.core.models import CameraState, FrameData
from visionguard.core.state_machine import CameraStateMachine
from visionguard.logging.logger import logger


class SyntheticObject:
    def __init__(self, obj_type: str, x: float, y: float, vx: float, vy: float, color: tuple) -> None:
        self.type = obj_type
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color

    def update(self, width: int, height: int) -> None:
        self.x += self.vx
        self.y += self.vy
        if self.x < 50 or self.x > width - 50:
            self.vx *= -1
        if self.y < 50 or self.y > height - 50:
            self.vy *= -1


class SyntheticVideoStream(BaseStream):
    """Synthetic test video stream generator."""

    def __init__(
        self,
        camera_id: str = "cam_01",
        width: int = 1280,
        height: int = 720,
        fps: float = 25.0,
    ) -> None:
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.state_machine = CameraStateMachine(camera_id)
        self.running = False
        self.frame_queue: Queue[FrameData] = Queue(maxsize=10)
        self.frame_counter = 0
        self._thread: Optional[Thread] = None

        self.objects: List[SyntheticObject] = [
            SyntheticObject("person", 100, 300, 3.5, 1.2, (255, 100, 0)),
            SyntheticObject("person", 600, 150, -2.0, 2.5, (0, 255, 100)),
            SyntheticObject("car", 400, 500, 4.0, 0.0, (100, 100, 255)),
        ]

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.state_machine.transition_to(CameraState.STREAMING, "Synthetic stream started")
        self._thread = Thread(target=self._capture_loop, daemon=True, name=f"synthetic_{self.camera_id}")
        self._thread.start()
        logger.info(f"SyntheticVideoStream [{self.camera_id}]: Started synthetic generator ({self.width}x{self.height} @ {self.fps} FPS)")

    def stop(self) -> None:
        self.running = False
        self.state_machine.transition_to(CameraState.STOPPED)

    def get_state(self) -> CameraState:
        return self.state_machine.current_state

    def read_frame(self) -> Optional[FrameData]:
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None

    def _capture_loop(self) -> None:
        frame_interval = 1.0 / self.fps

        while self.running:
            start_time = time.time()
            self.frame_counter += 1

            # Render synthetic background frame (dark grid)
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            frame[:] = (30, 30, 35)

            # Draw background grid lines
            for x in range(0, self.width, 80):
                cv2.line(frame, (x, 0), (x, self.height), (45, 45, 50), 1)
            for y in range(0, self.height, 80):
                cv2.line(frame, (0, y), (self.width, y), (45, 45, 50), 1)

            # Draw synthetic moving objects
            for obj in self.objects:
                obj.update(self.width, self.height)
                cx, cy = int(obj.x), int(obj.y)

                if obj.type == "person":
                    cv2.circle(frame, (cx, cy), 20, obj.color, -1)
                    cv2.putText(frame, "Person", (cx - 25, cy - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                elif obj.type == "car":
                    cv2.rectangle(frame, (cx - 40, cy - 20), (cx + 40, cy + 20), obj.color, -1)
                    cv2.putText(frame, "Car", (cx - 20, cy - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Draw OSD timestamp banner
            timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, f"SYNTHETIC STREAM - {timestamp_str} | Frame: {self.frame_counter}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            frame_data = FrameData(
                frame_id=self.frame_counter,
                camera_id=self.camera_id,
                timestamp=time.time(),
                image=frame,
                width=self.width,
                height=self.height,
                fps=self.fps,
            )

            if not self.frame_queue.full():
                self.frame_queue.put(frame_data)

            time.sleep(max(0.001, frame_interval - (time.time() - start_time)))
