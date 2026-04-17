#!/usr/bin/env python3
"""Minimal local camera capture utility for texas-holdem-robot."""

import argparse
import os
import sys
import time


def main():
    parser = argparse.ArgumentParser(description="Capture one frame from a local camera.")
    parser.add_argument("--device", type=int, default=0, help="Camera index to open.")
    parser.add_argument(
        "--output",
        default="/tmp/poker_latest.jpg",
        help="Path to write the captured image.",
    )
    args = parser.parse_args()

    try:
        import cv2
    except ImportError:
        print("Error: OpenCV is required. Install with: pip install opencv-python", file=sys.stderr)
        sys.exit(1)

    # The first cap.read() after an MJPG/resolution reconfigure can block on
    # a 10s V4L2 select() timeout. If that happens, release and reopen — a
    # fresh open usually succeeds on the next attempt.
    frame = None
    for attempt in range(4):
        cap = cv2.VideoCapture(args.device, cv2.CAP_V4L2)
        if not cap.isOpened():
            print(f"Error: could not open camera device {args.device}", file=sys.stderr)
            sys.exit(1)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        time.sleep(1.5)
        ok, f = cap.read()
        if ok and f is not None:
            # Warm up AE/AWB a few more frames.
            for _ in range(4):
                ok2, f2 = cap.read()
                if ok2 and f2 is not None:
                    f = f2
            frame = f
            cap.release()
            break
        cap.release()
        time.sleep(0.5)
    ok = frame is not None

    if not ok or frame is None:
        print("Error: failed to read a frame from the camera", file=sys.stderr)
        sys.exit(1)

    output_path = os.path.abspath(args.output)
    if not cv2.imwrite(output_path, frame):
        print(f"Error: failed to write image to {output_path}", file=sys.stderr)
        sys.exit(1)

    print(output_path)


if __name__ == "__main__":
    main()
