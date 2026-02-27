"""
Crowd Detection Engine
Supports two modes:
  1. Haar Cascade  — fast, CPU-only
  2. YOLO          — more accurate

Usage:
    engine = YOLODetector()   # or HaarDetector()
    count = engine.detect_from_frame(frame)
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class BaseDetector:
    def detect_from_frame(self, frame: np.ndarray) -> int:
        raise NotImplementedError

    def detect_from_camera(self, source=0, duration_seconds=5) -> int:
        """Open a camera, grab frames, return average person count."""
        try:
            import cv2
        except ImportError:
            logger.error("OpenCV not installed. Run: pip install opencv-python")
            return 0

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            logger.error(f"Cannot open camera source: {source}")
            return 0

        counts = []
        import time
        end_time = time.time() + duration_seconds

        while time.time() < end_time:
            ret, frame = cap.read()
            if not ret:
                break
            count = self.detect_from_frame(frame)
            counts.append(count)

        cap.release()
        return int(np.mean(counts)) if counts else 0


# ---------------------------------------------------------------------------
# Option 1: Haar Cascade
# ---------------------------------------------------------------------------

class HaarDetector(BaseDetector):
    """
    Simple, fast people detector using HOG + SVM.
    Requires: pip install opencv-python
    """

    def __init__(self):
        try:
            import cv2
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            logger.info("HaarDetector initialized.")
        except ImportError:
            self.hog = None
            logger.warning("OpenCV not available; HaarDetector in stub mode.")

    def detect_from_frame(self, frame: np.ndarray) -> int:
        if self.hog is None:
            return 0
        import cv2
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects, _ = self.hog.detectMultiScale(
            gray,
            winStride=(8, 8),
            padding=(4, 4),
            scale=1.05,
        )
        return len(rects)


# ---------------------------------------------------------------------------
# Option 2: YOLO
# ---------------------------------------------------------------------------

class YOLODetector(BaseDetector):
    """
    Accurate people detector using YOLOv8.

    Requirements:
        pip install ultralytics opencv-python

    Model weights are downloaded automatically on first run.
    You can also use a custom-trained model by passing model_path.
    """

    PERSON_CLASS_ID = 0  # COCO class 0 = person

    def __init__(self, model_path: str = 'yolov8n.pt', confidence: float = 0.4):
        self.confidence = confidence
        self.model = None
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            logger.info(f"YOLODetector initialized with model: {model_path}")
        except ImportError:
            logger.warning(
                "Ultralytics not installed. "
                "Run: pip install ultralytics   — YOLO detection disabled."
            )
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")

    def detect_from_frame(self, frame: np.ndarray) -> int:
        if self.model is None:
            return 0
        results = self.model(frame, verbose=False)
        count = 0
        for result in results:
            for box in result.boxes:
                if (
                    int(box.cls[0]) == self.PERSON_CLASS_ID
                    and float(box.conf[0]) >= self.confidence
                ):
                    count += 1
        return count

    def detect_with_visualization(self, frame: np.ndarray):
        """Returns (count, annotated_frame)."""
        if self.model is None:
            return 0, frame
        results = self.model(frame, verbose=False)
        count = 0
        annotated = frame.copy()
        import cv2
        for result in results:
            for box in result.boxes:
                if (
                    int(box.cls[0]) == self.PERSON_CLASS_ID
                    and float(box.conf[0]) >= self.confidence
                ):
                    count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        annotated,
                        f"Person {float(box.conf[0]):.0%}",
                        (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1,
                    )
        return count, annotated


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_detector(mode: str = 'yolo') -> BaseDetector:
    if mode == 'haar':
        return HaarDetector()
    return YOLODetector()
