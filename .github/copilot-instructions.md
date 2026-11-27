# Repository maintenance instructions

- Preserve the local Windows webcam workflow and the optional nature of YOLO person detection.
- Keep alert-policy tests independent of camera hardware.
- Run `python -m compileall -q src tests` and `python -m unittest discover -s tests -p 'test_*.py' -v` before proposing code changes.
- Do not claim real-camera accuracy, physical hand contact, or safety guarantees from offline tests.
- Preserve local frame processing and document any changes to data handling or third-party dependencies.
