"""Tests that run on any Python >=3.10, without a webcam or MediaPipe."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from alert_logic import AlertGate


class AlertGateTests(unittest.TestCase):
    def test_requires_consecutive_overlaps(self):
        gate = AlertGate(required_frames=3, cooldown_seconds=2.0)
        self.assertFalse(gate.observe(True, 10.0))
        self.assertFalse(gate.observe(True, 10.1))
        self.assertFalse(gate.observe(False, 10.2))
        self.assertFalse(gate.observe(True, 10.3))
        self.assertFalse(gate.observe(True, 10.4))
        self.assertTrue(gate.observe(True, 10.5))

    def test_respects_cooldown_without_resetting_consecutive_hits(self):
        gate = AlertGate(required_frames=2, cooldown_seconds=3.0)
        self.assertFalse(gate.observe(True, 100.0))
        self.assertTrue(gate.observe(True, 100.1))
        self.assertFalse(gate.observe(True, 101.0))
        self.assertFalse(gate.observe(True, 103.09))
        self.assertTrue(gate.observe(True, 103.1))

    def test_rejects_invalid_settings(self):
        for frames, cooldown in [(0, 1.0), (-1, 1.0), (2, -1.0), (2, float("inf"))]:
            with self.subTest(frames=frames, cooldown=cooldown):
                with self.assertRaises(ValueError):
                    AlertGate(frames, cooldown)

    def test_missing_face_or_hand_resets_touch_sequence(self):
        gate = AlertGate(required_frames=2, cooldown_seconds=0.0)
        self.assertFalse(gate.observe(True, 1.0))
        self.assertFalse(gate.observe(False, 1.1))
        self.assertFalse(gate.observe(True, 1.2))
        self.assertTrue(gate.observe(True, 1.3))


if __name__ == "__main__":
    unittest.main()
