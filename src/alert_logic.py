"""Pure, webcam-independent alert policy for deterministic regression tests."""
from dataclasses import dataclass


@dataclass
class AlertGate:
    required_frames: int
    cooldown_seconds: float
    consecutive: int = 0
    last_alert_at: float | None = None

    def __post_init__(self) -> None:
        if isinstance(self.required_frames, bool) or self.required_frames < 1:
            raise ValueError("required_frames must be a positive integer")
        if not (0 <= self.cooldown_seconds < float("inf")):
            raise ValueError("cooldown_seconds must be finite and nonnegative")

    def observe(self, overlap: bool, now: float) -> bool:
        """Return True only after enough consecutive hits and the cooldown."""
        if overlap:
            self.consecutive += 1
        else:
            self.consecutive = 0
            return False

        if self.consecutive < self.required_frames:
            return False
        if self.last_alert_at is not None and now - self.last_alert_at < self.cooldown_seconds:
            return False
        self.last_alert_at = now
        return True
