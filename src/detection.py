from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

try:
    from ultralytics import YOLO
except Exception:  # pragma: no cover
    YOLO = None


@dataclass
class DetectionConfig:
    use_yolo_person: bool
    yolo_model: str
    yolo_conf: float
    beard_roi_height_ratio: float


@dataclass
class DetectionResult:
    hand_touch: bool
    beard_roi: Optional[Tuple[int, int, int, int]]
    hand_boxes: Tuple[Tuple[int, int, int, int], ...]


class BeardTouchDetector:
    def __init__(self, config: DetectionConfig) -> None:
        self.config = config
        self.mp_face = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.mp_hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.yolo = None
        if self.config.use_yolo_person and YOLO is not None:
            self.yolo = YOLO(self.config.yolo_model)

    def _get_person_box(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        if self.yolo is None:
            return None
        results = self.yolo.predict(frame, conf=self.config.yolo_conf, verbose=False)
        if not results:
            return None
        best = None
        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                if int(box.cls[0].item()) != 0:
                    continue
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                score = float(box.conf[0].item())
                if best is None or score > best[0]:
                    best = (score, (x1, y1, x2, y2))
        return best[1] if best else None

    def _face_bbox(self, frame: np.ndarray, region: Optional[Tuple[int, int, int, int]]) -> Optional[Tuple[int, int, int, int]]:
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = region if region else (0, 0, w, h)
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return None
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        result = self.mp_face.process(rgb)
        if not result.multi_face_landmarks:
            return None
        lm = result.multi_face_landmarks[0].landmark
        xs = [int(p.x * (x2 - x1)) for p in lm]
        ys = [int(p.y * (y2 - y1)) for p in lm]
        fx1, fy1, fx2, fy2 = min(xs), min(ys), max(xs), max(ys)
        return (x1 + fx1, y1 + fy1, x1 + fx2, y1 + fy2)

    def _beard_roi(self, face_box: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        x1, y1, x2, y2 = face_box
        height = y2 - y1
        roi_h = int(height * self.config.beard_roi_height_ratio)
        by1 = max(y1, y2 - roi_h)
        return (x1, by1, x2, y2)

    def _hand_boxes(self, frame: np.ndarray, region: Optional[Tuple[int, int, int, int]]) -> Tuple[Tuple[int, int, int, int], ...]:
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = region if region else (0, 0, w, h)
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return tuple()
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        result = self.mp_hands.process(rgb)
        if not result.multi_hand_landmarks:
            return tuple()
        boxes = []
        for hand in result.multi_hand_landmarks:
            xs = [int(p.x * (x2 - x1)) for p in hand.landmark]
            ys = [int(p.y * (y2 - y1)) for p in hand.landmark]
            hx1, hy1, hx2, hy2 = min(xs), min(ys), max(xs), max(ys)
            boxes.append((x1 + hx1, y1 + hy1, x1 + hx2, y1 + hy2))
        return tuple(boxes)

    @staticmethod
    def _intersects(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> bool:
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return (ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1)

    def detect(self, frame: np.ndarray) -> DetectionResult:
        person_box = self._get_person_box(frame) if self.config.use_yolo_person else None
        face_box = self._face_bbox(frame, person_box)
        if face_box is None:
            return DetectionResult(False, None, tuple())
        beard = self._beard_roi(face_box)
        hands = self._hand_boxes(frame, person_box)
        touch = any(self._intersects(beard, h) for h in hands)
        return DetectionResult(touch, beard, hands)
