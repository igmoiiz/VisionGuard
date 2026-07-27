"""
VisionGuard Video Stream Manager.
Threaded OpenCV video capture manager supporting Webcams, USB cameras, RTSP/IP streams,
MP4/AVI video files, auto-reconnect logic, and automatic fallback to SyntheticVideoStream.
"""

from queue import Full, Queue
import time
from threading import Thread
from typing import Optional, Union
import cv2
from visionguard.camera.base_stream import BaseStream
from visionguard.camera.synthetic_stream import SyntheticVideoStream
from visionguard.core.models import CameraState, FrameData
from visionguard.core.state_machine import CameraStateMachine
from visionguard.logging.logger import logger


class StreamManager(BaseStream):
    """Threaded OpenCV frame reader with auto-reconnect and synthetic fallback."""

    def __init__(
        self,
        camera_id: str,
        source: str = "0",
        fps_target: float = 25.0,
        resolution: tuple = (1280, 720),
        reconnect_interval_sec: float = 5.0,
        buffer_size: int = 10,
    ) -> None:
        self.camera_id = camera_id
        self.source = source
        self.fps_target = fps_target
        self.resolution = resolution
        self.reconnect_interval_sec = reconnect_interval_sec
        self.buffer_size = buffer_size

        self.state_machine = CameraStateMachine(camera_id)
        self.frame_queue: Queue[FrameData] = Queue(maxsize=buffer_size)
        self.running = False
        self.frame_counter = 0
        self._cap: Optional[cv2.VideoCapture] = None
        self._thread: Optional[Thread] = None
        self._synthetic_fallback: Optional[SyntheticVideoStream] = None

    def start(self) -> None:
        if self.running:
            return

        self.running = True
        self.state_machine.transition_to(CameraState.CONNECTING, f"Opening source '{self.source}'")
        self._thread = Thread(target=self._capture_loop, daemon=True, name=f"stream_{self.camera_id}")
        self._thread.start()

    def stop(self) -> None:
        self.running = False
        if self._synthetic_fallback:
            self._synthetic_fallback.stop()
        self.state_machine.transition_to(CameraState.STOPPED)

    def get_state(self) -> CameraState:
        if self._synthetic_fallback:
            return self._synthetic_fallback.get_state()
        return self.state_machine.current_state

    def read_frame(self) -> Optional[FrameData]:
        if self._synthetic_fallback:
            return self._synthetic_fallback.read_frame()

        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None

    def _open_capture(self) -> bool:
        try:
            # Parse integer webcam index or string URI
            src_val: Union[int, str] = int(self.source) if self.source.isdigit() else self.source
            logger.info(f"StreamManager [{self.camera_id}]: Opening VideoCapture('{src_val}')...")
            self._cap = cv2.VideoCapture(src_val)

            if not self._cap.isOpened():
                logger.warning(f"StreamManager [{self.camera_id}]: Failed to open '{self.source}'.")
                return False

            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.state_machine.transition_to(CameraState.STREAMING, "VideoCapture opened")
            return True
        except Exception as e:
            logger.error(f"StreamManager [{self.camera_id}]: OpenCV VideoCapture error: {e}")
            return False

    def _capture_loop(self) -> None:
        success = self._open_capture()

        # Fallback to Synthetic Stream if hardware device fails
        if not success:
            logger.warning(f"StreamManager [{self.camera_id}]: Initiating fallback to SyntheticVideoStream...")
            self.state_machine.transition_to(CameraState.ERROR, "Physical camera unavailable")
            self._synthetic_fallback = SyntheticVideoStream(
                camera_id=self.camera_id,
                width=self.resolution[0],
                height=self.resolution[1],
                fps=self.fps_target,
            )
            self._synthetic_fallback.start()
            return

        frame_interval = 1.0 / max(1.0, self.fps_target)

        while self.running:
            if self._cap is None or not self._cap.isOpened():
                self.state_machine.transition_to(CameraState.ERROR, "Lost stream connection")
                time.sleep(self.reconnect_interval_sec)
                if not self._open_capture():
                    continue

            start_time = time.time()
            ret, frame = self._cap.read()

            if not ret or frame is None:
                # Video file loop or reconnect
                if self.source.endswith((".mp4", ".avi", ".mkv")):
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video file
                    continue
                else:
                    logger.warning(f"StreamManager [{self.camera_id}]: Frame read failed. Retrying...")
                    time.sleep(1.0)
                    continue

            self.frame_counter += 1
            h, w = frame.shape[:2]

            frame_data = FrameData(
                frame_id=self.frame_counter,
                camera_id=self.camera_id,
                timestamp=time.time(),
                image=frame,
                width=w,
                height=h,
                fps=self.fps_target,
            )

            try:
                self.frame_queue.put_nowait(frame_data)
            except Full:
                pass  # Drop oldest frame to ensure real-time latency on CPU

            time.sleep(max(0.001, frame_interval - (time.time() - start_time)))

        if self._cap:
            self._cap.release()
