from __future__ import annotations

import time
from pathlib import Path

import cv2
import yaml

from audio import play_alert
from detection import BeardTouchDetector, DetectionConfig
from alert_logic import AlertGate


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config.yaml"
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    cfg = load_config()
    det_cfg = DetectionConfig(
        use_yolo_person=bool(cfg.get("use_yolo_person")),
        yolo_model=str(cfg.get("yolo_model")),
        yolo_conf=float(cfg.get("yolo_conf")),
        beard_roi_height_ratio=float(cfg.get("beard_roi_height_ratio")),
    )
    detector = BeardTouchDetector(det_cfg)

    cap = cv2.VideoCapture(int(cfg.get("camera_index", 0)))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(cfg.get("frame_width", 1280)))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(cfg.get("frame_height", 720)))
    if not cap.isOpened():
        raise RuntimeError(
            f"Unable to open camera index {cfg.get('camera_index', 0)}. "
            "Check the camera connection, permissions, and config.yaml."
        )

    gate = AlertGate(
        required_frames=int(cfg.get("hand_touch_frames", 8)),
        cooldown_seconds=float(cfg.get("cooldown_seconds", 2.0)),
    )

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError("The camera stopped returning frames.")

            result = detector.detect(frame)
            if gate.observe(result.hand_touch, time.monotonic()):
                play_alert(cfg.get("sound_path", ""), int(cfg.get("beep_freq", 1200)), int(cfg.get("beep_duration_ms", 250)))

            if cfg.get("draw_debug", True):
                if result.beard_roi:
                    x1, y1, x2, y2 = result.beard_roi
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 255), 2)
                    cv2.putText(frame, "BEARD ROI", (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
                for (hx1, hy1, hx2, hy2) in result.hand_boxes:
                    cv2.rectangle(frame, (hx1, hy1), (hx2, hy2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"Touch frames: {gate.consecutive}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

            cv2.imshow("Beard Alert", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
