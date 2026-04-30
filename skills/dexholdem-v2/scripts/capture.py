#!/usr/bin/env python3
"""Reliable single-frame capture helper for DexHoldem V2."""

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone


def _load_config(path):
    if not path or not os.path.exists(path):
        return {}
    try:
        import yaml
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _write_meta(output_path, meta):
    meta_path = output_path + ".meta.json"
    tmp = meta_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(meta, f, indent=2)
    os.replace(tmp, meta_path)


def _copy_source(source, output, write_meta):
    output = os.path.abspath(output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    shutil.copy2(source, output)
    if write_meta:
        _write_meta(output, {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source": os.path.abspath(source),
            "mode": "source_copy",
        })
    print(output)


def _capture_camera(args, config):
    try:
        import cv2
    except ImportError:
        print("Error: opencv-python is required for camera capture", file=sys.stderr)
        return 1

    cap_cfg = config.get("capture", {}) or {}
    device = args.device if args.device is not None else int(cap_cfg.get("device", 0))
    width = int(args.width or cap_cfg.get("width", 1920))
    height = int(args.height or cap_cfg.get("height", 1080))
    warmup_frames = int(args.warmup_frames if args.warmup_frames is not None else cap_cfg.get("warmup_frames", 8))
    retries = int(args.retries if args.retries is not None else cap_cfg.get("retries", 3))
    retry_delay = float(args.retry_delay if args.retry_delay is not None else cap_cfg.get("retry_delay", 0.5))

    last_error = "capture not attempted"
    for attempt in range(1, retries + 1):
        cap = cv2.VideoCapture(device)
        if not cap.isOpened():
            last_error = f"could not open camera device {device}"
            cap.release()
            time.sleep(retry_delay)
            continue

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        frame = None
        ok = False
        for _ in range(max(warmup_frames, 0) + 1):
            ok, frame = cap.read()
            if ok and frame is not None:
                last_error = ""
        cap.release()

        if not ok or frame is None:
            last_error = "camera returned no frame"
            time.sleep(retry_delay)
            continue

        output = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(output), exist_ok=True)
        if not cv2.imwrite(output, frame):
            last_error = f"failed to write image to {output}"
            time.sleep(retry_delay)
            continue

        if args.meta:
            _write_meta(output, {
                "captured_at": datetime.now(timezone.utc).isoformat(),
                "device": device,
                "width": width,
                "height": height,
                "warmup_frames": warmup_frames,
                "attempt": attempt,
                "mode": "camera",
            })
        print(output)
        return 0

    print(f"Error: {last_error}", file=sys.stderr)
    return 1


def main():
    parser = argparse.ArgumentParser(description="Capture one DexHoldem table image.")
    parser.add_argument("--output", default="s_current/00_capture.jpg")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--source", help="Copy an existing image instead of reading a camera")
    parser.add_argument("--device", type=int)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--warmup-frames", type=int)
    parser.add_argument("--retries", type=int)
    parser.add_argument("--retry-delay", type=float)
    parser.add_argument("--meta", action="store_true", help="Write <output>.meta.json")
    args = parser.parse_args()

    if args.source:
        _copy_source(args.source, args.output, args.meta)
        return

    config = _load_config(args.config)
    raise SystemExit(_capture_camera(args, config))


if __name__ == "__main__":
    main()
