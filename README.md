# Beard Alert

Beard Alert is a local Windows webcam utility that plays an audible alert when a detected hand overlaps the lower-face region. It combines MediaPipe Face Mesh and Hands; optional YOLO person detection can narrow processing to the most prominent person.

> This is a computer-vision experiment, not a safety, medical, or biometric-identification system. Detection quality depends on camera angle, lighting, occlusion, and the configured thresholds.

## Features

- Real-time webcam processing with an on-screen debug overlay.
- Local lower-face ("beard") region estimation from face landmarks.
- Alert only after a configurable number of consecutive overlap frames.
- Windows beep by default, or an optional local WAV file.
- Optional YOLO person bounding box for scenes with multiple people.

## Requirements

- Windows 10/11 with a webcam and permission for Python to access it.
- Python 3.10–3.12.

## Quick start

From PowerShell in the project directory:

```powershell
.\run_beard_alert.ps1
```

The script creates `.venv`, installs the base dependencies, and starts the application. Press **Esc** in the webcam window to exit.

To run the commands manually:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/main.py
```

If PowerShell blocks local scripts, run the manual commands above instead of changing a system-wide execution policy.

## Configuration

Edit [`config.yaml`](config.yaml) before launching.

| Setting | Default | Purpose |
| --- | --- | --- |
| `camera_index` | `0` | Webcam index; use `1` or another value for an external camera. |
| `hand_touch_frames` | `8` | Consecutive detected overlap frames required before the alert. Increase it to reduce false alerts. |
| `cooldown_seconds` | `2.0` | Minimum delay between alerts. |
| `beard_roi_height_ratio` | `0.4` | Lower-face fraction used as the beard region. |
| `sound_path` | empty | Optional path to a local WAV sound; otherwise Windows plays a beep. |
| `draw_debug` | `true` | Shows the estimated beard region and hand boxes. |

### Optional YOLO person detection

The default configuration does **not** require or download YOLO. To enable it:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-yolo.txt
```

Then set `use_yolo_person: true` in `config.yaml`. Ultralytics may download the public `yolov8n.pt` checkpoint on its first use.

## Privacy

Frames are processed locally in memory. The application does not upload, transmit, or save webcam frames. Any configured local audio file remains on your machine and is excluded from Git by default practices.

## Troubleshooting

- **Unable to open camera**: close other applications using the webcam, check Windows camera permissions, and try a different `camera_index`.
- **No alert**: enable `draw_debug`, make sure a face and hand are visible, then lower `hand_touch_frames` or raise `beard_roi_height_ratio` carefully.
- **YOLO enabled but unavailable**: install `requirements-yolo.txt` or set `use_yolo_person: false`.

## License

The source code is released under the [MIT License](LICENSE). Third-party Python packages and optional YOLO weights retain their respective licenses.
