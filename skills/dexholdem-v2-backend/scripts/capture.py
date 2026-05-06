#!/usr/bin/env python3
"""Reliable single-frame capture helper for DexHoldem V2."""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

from utils import atomic_copy, atomic_image_write, atomic_write_json, load_config

DEFAULT_WARMUP_FRAMES = 60
DEFAULT_TIMEOUT = 15


def _write_meta(output_path, meta):
    atomic_write_json(output_path + ".meta.json", meta)


def _copy_source(source, output, write_meta):
    output = os.path.abspath(output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    atomic_copy(source, output)
    if write_meta:
        _write_meta(output, {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source": os.path.abspath(source),
            "mode": "source_copy",
        })
    print(output)


def _configured_capture(args, config):
    cap_cfg = config.get("capture", {}) or {}
    return {
        "backend": args.backend or cap_cfg.get("backend", "auto"),
        "device": args.device if args.device is not None else int(cap_cfg.get("device", 0)),
        "width": int(args.width or cap_cfg.get("width", 1920)),
        "height": int(args.height or cap_cfg.get("height", 1080)),
        "warmup_frames": int(
            args.warmup_frames
            if args.warmup_frames is not None
            else cap_cfg.get("warmup_frames", DEFAULT_WARMUP_FRAMES)
        ),
        "retries": int(args.retries if args.retries is not None else cap_cfg.get("retries", 3)),
        "retry_delay": float(args.retry_delay if args.retry_delay is not None else cap_cfg.get("retry_delay", 0.5)),
        "timeout": float(args.timeout if args.timeout is not None else cap_cfg.get("timeout", DEFAULT_TIMEOUT)),
    }


def _video_devices():
    devices = []
    for path in sorted(glob.glob("/dev/video*")):
        match = re.fullmatch(r"/dev/video(\d+)", path)
        if match:
            devices.append(int(match.group(1)))
    return devices


def _is_capture_device(device):
    path = f"/dev/video{device}"
    if shutil.which("v4l2-ctl") is None:
        return os.path.exists(path)
    try:
        result = subprocess.run(
            ["v4l2-ctl", "-d", path, "--all"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return os.path.exists(path)
    if result.returncode != 0:
        return False
    device_caps = result.stdout.split("Device Caps", 1)[-1]
    return "Video Capture" in device_caps


def _ordered_capture_devices(preferred):
    devices = [device for device in _video_devices() if _is_capture_device(device)]
    if preferred in devices:
        devices.remove(preferred)
        devices.insert(0, preferred)
    elif os.path.exists(f"/dev/video{preferred}") and _is_capture_device(preferred):
        devices.insert(0, preferred)
    return devices


def _parse_ffmpeg_resolution(stderr, width, height):
    for line in stderr.splitlines():
        if "Stream" not in line or "Video" not in line:
            continue
        match = re.search(r"\s(\d{3,5})x(\d{3,5})[,\s]", line)
        if match:
            return int(match.group(1)), int(match.group(2))
    return width, height


def _capture_ffmpeg(output, device, width, height, warmup_frames, timeout):
    if shutil.which("ffmpeg") is None:
        return False, {"error": "ffmpeg not found on PATH"}

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "info",
        "-y",
        "-f",
        "v4l2",
        "-video_size",
        f"{width}x{height}",
        "-i",
        f"/dev/video{device}",
        "-frames:v",
        str(max(warmup_frames, 0) + 1),
        "-update",
        "1",
        output,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return False, {"error": f"ffmpeg timed out after {timeout:g}s"}
    except Exception as exc:
        return False, {"error": repr(exc)}

    if os.path.exists(output) and os.path.getsize(output) > 0:
        actual_width, actual_height = _parse_ffmpeg_resolution(result.stderr, width, height)
        return True, {
            "device": device,
            "width": actual_width,
            "height": actual_height,
            "stderr_tail": result.stderr[-1000:],
        }
    return False, {
        "error": f"ffmpeg exited {result.returncode} without writing an image",
        "stderr_tail": result.stderr[-1000:],
    }


def _capture_opencv(output, device, width, height, warmup_frames):
    try:
        import cv2
    except ImportError:
        return False, {"error": "opencv-python is not installed"}

    cap = cv2.VideoCapture(device)
    try:
        if not cap.isOpened():
            return False, {"error": f"could not open camera device {device}"}

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        frame = None
        ok = False
        for _ in range(max(warmup_frames, 0) + 1):
            ok, frame = cap.read()
        if not ok or frame is None:
            return False, {"error": "camera returned no frame"}
        if not cv2.imwrite(output, frame):
            return False, {"error": f"failed to write image to {output}"}
        return True, {"device": device, "width": width, "height": height}
    finally:
        cap.release()


def _capture_once(output, backend, device, width, height, warmup_frames, timeout):
    if backend == "ffmpeg":
        ok, detail = _capture_ffmpeg(output, device, width, height, warmup_frames, timeout)
        return ok, "ffmpeg", detail
    if backend == "opencv":
        ok, detail = _capture_opencv(output, device, width, height, warmup_frames)
        return ok, "opencv", detail

    ffmpeg_ok, ffmpeg_detail = _capture_ffmpeg(output, device, width, height, warmup_frames, timeout)
    if ffmpeg_ok:
        return True, "ffmpeg", ffmpeg_detail
    opencv_ok, opencv_detail = _capture_opencv(output, device, width, height, warmup_frames)
    if opencv_ok:
        return True, "opencv", opencv_detail
    return False, "auto", {"ffmpeg": ffmpeg_detail, "opencv": opencv_detail}


def _capture_camera(args, config):
    cfg = _configured_capture(args, config)
    devices = _ordered_capture_devices(cfg["device"])
    if not devices:
        print("Error: no video capture devices found", file=sys.stderr)
        return 1

    last_error = "capture not attempted"
    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    for attempt in range(1, cfg["retries"] + 1):
        for device in devices:
            detail = {}
            backend_used = cfg["backend"]
            try:
                ok = False

                def write_frame(tmp):
                    nonlocal detail, backend_used, ok
                    ok, backend_used, detail = _capture_once(
                        tmp,
                        cfg["backend"],
                        device,
                        cfg["width"],
                        cfg["height"],
                        cfg["warmup_frames"],
                        cfg["timeout"],
                    )
                    return ok

                atomic_image_write(output, write_frame)
            except RuntimeError:
                last_error = f"device {device}: {detail or {'error': 'failed to write image'}}"
                time.sleep(cfg["retry_delay"])
                continue

            if ok:
                if args.meta:
                    _write_meta(output, {
                        "captured_at": datetime.now(timezone.utc).isoformat(),
                        "device": detail.get("device", device),
                        "width": detail.get("width", cfg["width"]),
                        "height": detail.get("height", cfg["height"]),
                        "warmup_frames": cfg["warmup_frames"],
                        "attempt": attempt,
                        "backend": backend_used,
                        "mode": "camera",
                    })
                print(output)
                return 0

    print(f"Error: {last_error}", file=sys.stderr)
    return 1


def _preflight(config):
    cfg = _configured_capture(argparse.Namespace(
        backend=None,
        device=None,
        width=None,
        height=None,
        warmup_frames=0,
        retries=1,
        retry_delay=None,
        timeout=None,
    ), config)
    print("Camera Preflight")
    print(f"ffmpeg: {shutil.which('ffmpeg') or 'not found'}")
    print(f"opencv-python: {'available' if _opencv_available() else 'not installed'}")
    print("devices:")
    for device in _video_devices():
        label = "capture" if _is_capture_device(device) else "not video-capture"
        print(f"  /dev/video{device}: {label}")
    return 0 if _ordered_capture_devices(cfg["device"]) else 1


def _opencv_available():
    try:
        import cv2  # noqa: F401
    except ImportError:
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Capture one DexHoldem table image.")
    parser.add_argument("--output", default="s_current/00_capture.jpg")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--source", help="Copy an existing image instead of reading a camera")
    parser.add_argument("--device", type=int)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--backend", choices=("auto", "ffmpeg", "opencv"))
    parser.add_argument("--warmup-frames", type=int)
    parser.add_argument("--retries", type=int)
    parser.add_argument("--retry-delay", type=float)
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--preflight", action="store_true", help="Print camera/backend diagnostics")
    parser.add_argument("--meta", action="store_true", help="Write <output>.meta.json")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.preflight:
        raise SystemExit(_preflight(config))

    if args.source:
        _copy_source(args.source, args.output, args.meta)
        return

    raise SystemExit(_capture_camera(args, config))


if __name__ == "__main__":
    main()
