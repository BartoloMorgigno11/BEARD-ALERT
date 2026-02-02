from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import winsound  # Windows only
except Exception:  # pragma: no cover
    winsound = None


def play_alert(sound_path: Optional[str], beep_freq: int, beep_duration_ms: int) -> None:
    if sound_path:
        path = Path(sound_path)
        if path.exists() and winsound is not None:
            try:
                winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
            except Exception:
                pass
    if winsound is not None:
        winsound.Beep(beep_freq, beep_duration_ms)
